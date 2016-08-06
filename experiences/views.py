import json

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from django.conf import settings
from django.forms import modelform_factory
from django.db import InternalError
from django.core.mail import EmailMultiAlternatives

from experiences.models import Experience, FeaturedExperience
from experiences.forms import ExperienceForm, ExperienceBriefForm
from narratives.models import Narrative
from narratives.forms import NarrativeForm, NarrativeTransferForm, TRANSFER_ACTION_CHOICES
from notifications import notify
from paypal.standard.forms import PayPalPaymentsForm


def index(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    privileged = request.user in experience.explorers.all()
    if request.get_signed_cookie('experience_password', salt='personal_domain', default=False):
        if (
            request.get_signed_cookie('experience_password', salt='personal_domain') ==
            str(experience_id)
        ):
            privileged = True
    if not experience.is_public:
        if not privileged:
            if experience.password:
                # Give them the option of providing password
                return redirect(reverse('check_password', args=(experience_id,)))
            else:
                raise PermissionDenied
    if experience.narratives.filter(is_public=False):
        if privileged:
            narratives = experience.ordered_narratives()
        else:
            narratives = experience.ordered_narratives().filter(is_public=True)
    else:
        narratives = experience.ordered_narratives()
    narrative_form = None
    if request.user in experience.explorers.all():
        narrative_form = NarrativeForm(author=request.user)
    experience_brief_form = None
    if not experience.brief:
        experience_brief_form = ExperienceBriefForm(instance=experience)
    paypal_form = None
    if experience.accepts_paypal:
        paypal_dict = {
            'business': experience.author.email,
            'amount': "25.00",
            'item_name': experience,
            'invoice': 'unique-invoice-id',
            'cmd': '_donations',
            'bn': 'Acressity_Donate_WPS_US',
            'alt': 'Donate',
            'notify_url': 'https://www.example.com' + reverse('paypal-ipn'),
            'return_url': 'https://www.example.com/your-return-location/',
            'cancel_return': 'https://www.example.com/your-cancel-location/',
        }
        paypal_form = PayPalPaymentsForm(initial=paypal_dict, button_type='donate')
    context = {
        'experience': experience,
        'narratives': narratives,
        'author': experience.is_author(request),
        'privileged': privileged,
        'narrative_form': narrative_form,
        'experience_brief_form': experience_brief_form,
        'paypal_form': paypal_form,
    }
    return render(request, 'experiences/index.html', context)


@login_required
def create(request):
    if request.method == 'POST':
        form = ExperienceForm(request.POST, request=request,
                author=request.user)
        if form.is_valid():
            new_experience = form.save()
            if form.cleaned_data['make_feature']:
                request.user.featured_experience = form.instance
                request.user.save()
                messages.success(
                    request,
                    _('Your featured experience is now {0}'.format(
                        form.instance.experience))
                )
            elif form.cleaned_data['unfeature']:
                request.user.featured_experience = None
                request.user.save()
            # Notify me so I can congratulate them personally!
            to = settings.ADMINS[0][1]
            from_email = 'acressity@acressity.com'
            subject = 'New Experience!'
            text_content = '{0} has created a new experience: {1}!'.format(request.user, new_experience)
            message = EmailMultiAlternatives(subject, text_content, from_email, [to])
            message.send()
            if 'ajax' in request.POST:
                html = '<hr />'
                html += render_to_string(
                    'experiences/snippets/dash.html',
                    {
                        'experience': new_experience,
                        'user': request.user,
                        'STATIC_URL': settings.STATIC_URL
                    }
                )
                data = {'html': html}
                return HttpResponse(json.dumps(data))
            messages.success(request, _('Experience successfully added'))
            return redirect(reverse('experience', args=(new_experience.id,)))
    else:
        form = ExperienceForm()
    return render(request, 'experiences/create.html', {'form': form})


def edit(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.user in experience.explorers.all():
        if request.method == 'POST':
            form = ExperienceForm(
                request.POST,
                instance=experience,
                request=request
            )
            if form.is_valid():
                if form.cleaned_data['make_feature']:
                    request.user.featured_experience = form.instance
                    request.user.save()
                    messages.success(
                        request,
                        _('Your featured experience is now {0}'.format(form.instance)))
                elif form.cleaned_data['unfeature']:
                    request.user.featured_experience = None
                    request.user.save()
                if 'is_public' in request.POST:
                    if experience.author != request.user:
                        raise PermissionDenied
                form.save()
                messages.success(
                    request,
                    _('Experience has been successfully edited')
                )
                for comrade in experience.comrades(request):
                    notify.send(sender=request.user, recipient=comrade,
                                target=experience, verb='has edited your shared experience')
                return redirect(reverse('experience', args=(experience.id,)))
        else:
            form = ExperienceForm(instance=experience)
        return render(request, 'experiences/edit.html', {'form': form, 'experience': experience})
    else:
        raise PermissionDenied


def brief(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.is_ajax():
        form = ExperienceBriefForm(request.GET, instance=experience)
        if form.is_valid():
            form.save()
            return HttpResponse(json.dumps({'success': True, 'brief': form.cleaned_data.get('brief')}))
    if request.method == 'POST':
        form = ExperienceBriefForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(
                request, _('Experience brief was successfully added'))
            return redirect(reverse('experience', args=(experience_id,)))
    else:
        form = None
    if not experience.brief:
        form = ExperienceBriefForm(instance=experience)
    return render(request, 'experiences/brief.html', {'experience': experience, 'form': form})


def delete(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if experience.author == request.user:
        if request.method == 'POST':
            if 'nominate' in request.POST:
                new_author = get_object_or_404(
                    get_user_model(), pk=request.POST.get('explorer_id'))
                experience.author = new_author
                experience.explorers.remove(request.user)
                experience.save()
                messages.success(request, _(
                    '{0} is the new author and you have been removed from {1}'
                        .format(new_author, experience))
                )
                notify.send(sender=request.user, recipient=new_author,
                            target=experience, verb='has made you the new author of the experience')
                return redirect(reverse('journey', args=(request.user.id,)))
            elif 'confirm' in request.POST:
                for comrade in experience.comrades(request):
                    notify.send(sender=request.user, recipient=comrade,
                                target=experience, verb='has deleted the experience')
                experience.delete()
                messages.success(
                    request, 'Experience {0} was deleted'.format(experience))
                return redirect(reverse('journey', args=(request.user.id,)))
        else:
            return render(
                request,
                'experiences/delete.html',
                {'experience': Experience.objects.get(pk=experience_id)}
            )
    else:
        raise PermissionDenied


@login_required
def leave_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.user in experience.explorers.all():
        # They are a comrade. This option is not available to author
        if 'delete' in request.POST:
            # Cascade delete all of their presence in experience
            pass
        else:
            # Just remove them from experience.explorers
            pass
    else:
        raise PermissionDenied
    return redirect(reverse('journey', args=(request.user.id,)))


def categorize(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if experience in request.user.experiences.all():
        narratives = experience.narratives.all()
        if request.method == 'POST':
            for narrative, category in zip(narratives, request.POST.getlist('category')):
                if narrative.category != category:
                    narrative.category = category
                    narrative.save()
            return redirect('/experiences/{0}/categorize/'.format(experience.id))
        else:
            narratives_forms = []
            for narrative in narratives:
                form = NarrativeForm(author=experience.author, instance=narrative)
                narratives_forms.append((narrative, form))
        return render(
            request,
            'experiences/categorize.html',
            {'narratives_forms': narratives_forms}
        )
    else:
        raise PermissionDenied


def donate(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    paypal_form = None
    if experience.accepts_paypal:
        paypal_dict = {
            'business': experience.author.email,
            'amount': 25.00,
            'item_name': experience,
            'invoice': 'unique-invoice-id',
            'cmd': '_donations',
            'bn': 'Acressity_Donate_WPS_US',
            'alt': 'Donate',
            'notify_url': reverse('paypal-ipn'),
            # 'return': reverse('paypal_return'),
            'cancel_return': reverse('experience', args=(experience.id,)),
        }
        paypal_form = PayPalPaymentsForm(initial=paypal_dict, button_type='donate')
    return render(request, 'experiences/donate.html', {'experience': experience, 'paypal_form': paypal_form})


def paypal_return(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    return redirect(reverse('index'))


def featured(request):
    # I should export this to a generic view...
    featured_experiences = FeaturedExperience.objects.get_random(5)
    return render(
        request,
        'experiences/featured.html',
        {'featured_experiences': featured_experiences}
    )


@login_required
def transfer_narratives(request, experience_id):
    from_experience = get_object_or_404(Experience, pk=experience_id)

    if request.user not in from_experience.explorers.all():
        raise PermissionDenied

    other_experiences = request.user.experiences.exclude(pk=experience_id)
    NewExperienceForm = modelform_factory(Experience, form=ExperienceForm, fields=('experience',))

    if request.method == 'POST':
        if request.POST.get('new_experience'):
            to_experience = NewExperienceForm(request.POST, request=request,
                    author=request.user).save()
        elif request.POST.get('to_experience_id'):
            to_experience = get_object_or_404(Experience, pk=request.POST.get('to_experience_id'))

        if request.user not in to_experience.explorers.all():
            raise PermissionDenied

        action_choices = {index: value for index, value in TRANSFER_ACTION_CHOICES[1:]}

        num_copies = 0
        num_transfers = 0
        for narrative_id, action_index in zip(request.POST.getlist('narrative_ids'), request.POST.getlist('potential_actions')):
            if action_index:
                action = action_choices[int(action_index)]
                narrative = get_object_or_404(Narrative, pk=int(narrative_id))

                if narrative not in from_experience.narratives.all():
                    raise PermissionDenied

                if action == 'Transfer':
                    try:
                        to_experience.narratives.add(narrative)
                        num_transfers += 1
                    except:
                        raise InternalError('Sorry, something went wrong')
                elif action == 'Copy':
                    try:
                        # Fairly obscure way of copying the object seemingly demanded by Django
                        narrative.pk = None
                        narrative.experience = to_experience
                        narrative.save()
                        num_copies += 1
                    except:
                        raise InternalError('Sorry, something went wrong')
                
        if num_copies + num_transfers > 0:
            msg = 'Successfully '
            if num_copies:
                msg += 'copied {0} narrative{1} '.format(num_copies, '' if num_copies == 1 else 's')
                if num_transfers:
                    msg += 'and '
            if num_transfers:
                msg += 'transferred {0} narrative{1} '.format(num_transfers, '' if num_transfers == 1 else 's')
            msg += 'to {0}'.format(to_experience)
            messages.success(request, _(msg))
            return redirect(reverse('experience', args=(to_experience.id,)))

    narrative_forms = [NarrativeTransferForm(instance=n) for n in from_experience.narratives.all()]
    context = {
        'experience': from_experience,
        'other_experiences': other_experiences,
        'narrative_forms': narrative_forms,
        'new_experience_form': NewExperienceForm(),
    }
    return render(request, 'experiences/transfer_narratives.html', context)


def gallery(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    object_list = experience.get_galleries()
    return render(request, 'photologue/gallery_list.html', {'object_list': object_list})


def upload_photo(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if experience in request.user.experiences.all():
        if experience.gallery:
            gallery = experience.gallery
        else:
            gallery = experience.create_gallery()
            for explorer in experience.explorers.all():
                gallery.explorers.add(explorer)
            experience.gallery = gallery
            experience.save()
        return redirect(
            '/photologue/gallery/{0}/upload_photo/'.format(gallery.id)
        )
    else:
        raise PermissionDenied


def check_password(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == 'POST':
        password = request.POST.get('password')
        if experience.password == password:
            messages.success(
                request,
                _('''Welcome to the privileged side of things. Your privileged
                    state will expire at some point, requiring a reentry of the
                     password.''')
            )
            response = redirect(reverse('experience', args=(experience.id,)))
            response.set_signed_cookie(
                'experience_password',
                str(experience.id),
                salt='personal_domain')
            return response
        else:
            raise PermissionDenied
    return render(
        request,
        'experiences/check_password.html',
        {'experience': experience}
    )

def ajax_thing(request):
    experience = Experience.objects.get(pk=request.GET['exp_id'])
    d = {'thing_two': experience.title}

    json_val = json.dumps(d)
    return HttpResponse(json_val, mimetype='application/json')
