from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied

from experiences.models import Experience, FeaturedExperience
from narratives.models import Narrative
from experiences.forms import ExperienceForm, ExperienceBriefForm
from narratives.forms import NarrativeForm
from photologue.models import Gallery
from explorers.models import Explorer
from support.models import InvitationRequest


@login_required
def create(request):
    if request.method == 'POST':
        form = ExperienceForm(request.POST, request=request)
        if form.is_valid():
            form.save(commit=False)
            form.instance.author = request.user
            new_experience = form.save()
            form.instance.explorers.add(request.user)
            if form.cleaned_data['make_feature']:
                request.user.featured_experience = form.instance
                request.user.save()
                messages.success(request, 'Your featured experience is now {0}'.format(form.instance.experience))
            messages.success(request, 'Experience successfully added')
            return redirect(reverse('experience', args=(new_experience.id,)))
        # else:
        #     messages.error(request, 'There was an error in saving your new experience')
    else:
        form = ExperienceForm()
    return render(request, 'experiences/create.html', {'form': form})


def index(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if experience.is_public is False:
        if request.user not in experience.explorers.all():
            if request.get_signed_cookie('experience_password', salt='personal_domain', default=False):
                if request.get_signed_cookie('experience_password', salt='personal_domain') == str(experience_id):
                    pass
            else:
                #return HttpResponse('still here')
                # Give them the option of providing password
                return redirect(reverse('check_password', args=(experience_id,)))
    if experience.is_comrade(request):
        comrade = True
    else:
        comrade = False
    if comrade:
        form = NarrativeForm(request.user)
    else:
        form = None
    if not experience.brief:
        experience_brief_form = ExperienceBriefForm(instance=experience)
    else:
        experience_brief_form = None
    if request.user in experience.explorers.all():
        comrade = True
    return render(request, 'experiences/index.html', {'experience': experience, 'author': experience.is_author(request), 'comrade': comrade, 'form': form, 'experience_brief_form': experience_brief_form})


def edit(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if experience.is_comrade(request):
        if request.method == 'POST':
            form = ExperienceForm(request.POST, instance=experience, request=request)
            if form.is_valid():
                if form.cleaned_data['make_feature']:
                    request.user.featured_experience = form.instance
                    request.user.save()
                    messages.success(request, 'Your featured experience is now {0}'.format(form.instance))
                if 'is_public' in request.POST:
                    if experience.author != request.user:
                        raise PermissionDenied
                form.save()
                messages.success(request, 'Experience has been successfully edited')
                return redirect(reverse('experience', args=(experience.id,)))
        else:
            form = ExperienceForm(instance=experience)
            # if experience.gallery:
            #     form.fields['featured_photo'].queryset = experience.gallery.children_photos()
        return render(request, 'experiences/edit.html', {'form': form, 'experience': experience})
    else:
        raise PermissionDenied


def brief(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == 'POST':
        form = ExperienceBriefForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(request, 'Experience brief was successfully added')
            return redirect('/experiences/{0}'.format(experience.id))
    else:
        form = None
    if not experience.brief:
        form = ExperienceBriefForm(instance=experience)
    return render(request, 'experiences/brief.html', {'experience': experience, 'form': form})


def home(request):
    if request.user.is_authenticated():
        experiences = Experience.objects.filter(explorer_id=request.user.id)
    featured_experiences = Experience.objects.filter(is_feature=True)
    return render(request, 'experiences/home.html', {'experiences': experiences, 'featured_experiences': featured_experiences})


def delete(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if experience.author == request.user:
        if request.method == 'POST':
            if 'nominate' in request.POST:
                new_author = get_object_or_404(get_user_model(), pk=request.POST.get('explorer_id'))
                experience.author = new_author
                experience.explorers.remove(request.user)
                experience.save()
                messages.success(request, '{0} is the new author and you have been removed from {1}'.format(new_author, experience))
                return redirect(reverse('journey', args=(request.user.id,)))
            elif 'confirm' in request.POST:
                experience.delete()
                messages.success(request, 'Experience {0} was deleted'.format(experience))
                return redirect(reverse('journey', args=(request.user.id,)))
        else:
            return render(request, 'experiences/delete.html', {'experience': Experience.objects.get(pk=experience_id)})
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
                form = NarrativeForm(experience.author, instance=narrative)
                narratives_forms.append((narrative, form))
        return render(request, 'experiences/categorize.html', {'narratives_forms': narratives_forms})
    else:
        raise PermissionDenied


def featured(request):
    # I should export this to a generic view...
    featured_experiences = FeaturedExperience.objects.get_random(5)
    # for experience in featured_experiences:
    #     explorer = experience.experience.author
    #     explorer_experience.append((explorer, experience))
    return render(request, 'experiences/featured.html', {'featured_experiences': featured_experiences})


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
            # gallery = Gallery(title=experience, content_type=ContentType.objects.get(model='experience'), object_pk=experience.id, is_public=experience.is_public)
            # gallery.save()
            for explorer in experience.explorers.all():
                gallery.explorers.add(explorer)
            experience.gallery = gallery
            experience.save()
        return redirect('/photologue/gallery/{0}/upload_photo/'.format(gallery.id))
    else:
        raise PermissionDenied


def check_password(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == 'POST':
        password = request.POST.get('password')
        if experience.password == password:
            response = render(request, 'experiences/index.html', {'experience': experience})
            response.set_signed_cookie('experience_password', str(experience.id), salt='personal_domain')
            return response
        else:
            raise PermissionDenied
    return render(request, 'experiences/check_password.html', {'experience': experience})
