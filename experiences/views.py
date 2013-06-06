from experiences.models import Experience, FeaturedExperience
from narratives.models import Narrative
from experiences.forms import ExperienceForm, ExperienceBriefForm
from narratives.forms import NarrativeForm
from photologue.models import Gallery
from explorers.models import Explorer, Request

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType


def create(request):
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.instance.author = request.user
            form.save()
            form.instance.explorers.add(request.user)
            if form.cleaned_data['make_feature']:
                request.user.featured_experience = form.instance
                request.user.save()
                messages.success(request, 'Your featured experience is now {0}'.format(form.instance.experience))
            messages.success(request, 'Experience successfully added')
            if not form.instance.brief:
                return redirect('/experiences/{0}/brief/'.format(form.instance.id))
        else:
            messages.error(request, 'Form was not properly filled out')
            return redirect('/{0}/'.format(request.user.id), {'form': form})
        return redirect('/experiences/{0}/'.format(form.instance.id))


def index(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
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
            form = ExperienceForm(request.POST, instance=experience)
            if form.is_valid():
                if form.cleaned_data['make_feature']:
                    request.user.featured_experience = form.instance
                    request.user.save()
                    messages.success(request, 'Your featured experience is now {0}'.format(form.instance))
                form.save()
                messages.success(request, 'Experience has been successfully edited')
                return redirect(reverse('journey', args=(request.user.id,)))
            else:
                return HttpResponse(form.errors)
        else:
            form = ExperienceForm(instance=experience)
            # if experience.gallery:
            #     form.fields['featured_photo'].queryset = experience.gallery.children_photos()
        return render(request, 'experiences/edit.html', {'form': form, 'experience': experience})
    else:
        messages.error(request, 'Nice try on security breach! I would, however, love it if you did inform me of a website security weakness should (when) you find one.')
        return render(request, 'acressity/message.html')


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
    experience = Experience.objects.get(pk=experience_id)
    if experience.author == request.user:
        if request.method == 'POST' and 'confirm' in request.POST:
            experience.delete()
            messages.success(request, 'Experience {0} was deleted'.format(experience))
            return redirect(reverse('journey', args=(request.user.id,)))
        else:
            return render(request, 'experiences/delete.html', {'experience': Experience.objects.get(pk=experience_id)})
    else:
        messages.error(request, 'Nice try on security breach! I would, however, love it if you did inform me of a website security weakness should (when) you find one.')
        return render(request, 'acressity/message.html')


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
        messages.error(request, 'Nice try on security breach! I would, however, love it if you did inform me of a website security weakness should (when) you find one.')
        return render(request, 'acressity/message.html')


def invite(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.user != experience.author:
        messages.error(request, 'Sorry, you do not have the ability of inviting others to this experience')
        return render(request, 'acressity/message.html')
    explorers = Explorer.objects.exclude(experiences=experience).exclude(experience_recruit__experience=experience)  # Remove those who are already a part of the experience and those who have an outstanding request
    if request.method == 'POST':
        if 'invite' in request.POST:
            recruit = Explorer.objects.get(pk=int(request.POST.get('explorer_id')))
            experience_request = Request(author=request.user, recruit=recruit, experience=experience)
            experience_request.save()
            messages.success(request, 'You have invited {0} to be a part of {1}. How nice.'.format(recruit.get_full_name(), experience))
        elif 'email' in request.POST:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            if first_name and last_name and email:
                send_mail('Invitation from {0}'.format(request.user.get_full_name()), 'You have been invited to participate in the experience of {0}'.format(experience), 'acressity@acressity.com', [email])
                messages.success(request, 'You have successfully invited {0} {1}'.format(first_name, last_name))
        return redirect(reverse('experience', args=(experience.id,)))
    return render(request, 'experiences/invite.html', {'experience': experience, 'explorers': explorers})


def featured(request):
    explorer_experience = []
    featured_experiences = FeaturedExperience.objects.get_random(5)
    for experience in featured_experiences:
        explorer = experience.experience.author
        explorer_experience.append((explorer, experience))
    return render(request, 'experiences/featured.html', {'explorer_experience': explorer_experience})


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
            gallery = Gallery(title=experience, content_type=ContentType.objects.get(model='experience'), object_pk=experience.id)
            gallery.save()
            for explorer in experience.explorers.all():
                gallery.explorers.add(explorer)
            experience.gallery = gallery
            experience.save()
        return redirect('/photologue/gallery/{0}/upload_photo/'.format(gallery.id))
    else:
        messages.error(request, 'Nice try on security breach! I would, however, love it if you did inform me of a website security weakness should (when) you find one.')
        return render(request, 'acressity/message.html')