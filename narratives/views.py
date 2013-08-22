from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied

from narratives.models import Narrative
from narratives.forms import NarrativeForm
from experiences.models import Experience
from photologue.models import Gallery


def index(request, narrative_id):
    narrative = get_object_or_404(Narrative, pk=narrative_id)
    if not narrative.experience.is_public:
        if request.user not in narrative.experience.explorers.all():
            raise PermissionDenied
    return render(request, 'narratives/index.html', {'narrative': narrative, 'author': narrative.is_author(request)})


def create(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == 'POST' and experience.is_comrade(request):
        form = NarrativeForm(request.user, request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.instance.author = request.user
            new_narrative = form.save()
            messages.success(request, 'Your narrative has been added')
            return redirect('/narratives/{0}'.format(new_narrative.id))
    else:
        form = NarrativeForm(request.user, initial={'experience': experience.id})
    return render(request, 'narratives/create.html', {'form': form, 'experience': experience})


def edit(request, narrative_id):
    narrative = get_object_or_404(Narrative, pk=narrative_id)
    if narrative.author == request.user:
        if request.method == 'POST':
            form = NarrativeForm(narrative.author, request.POST, instance=narrative)
            if form.is_valid():
                form.save()
                messages.success(request, 'Narrative successfully updated')
                return redirect('/narratives/{0}'.format(narrative.id))
        else:
            form = NarrativeForm(narrative.author, instance=narrative)
        return render(request, 'narratives/edit.html', {'form': form, 'narrative': narrative})
    else:
        messages.error(request, 'Nice try on security breach! I would, however, love it if you did inform me of a website security weakness should (when) you find one.')
        return render(request, 'acressity/message.html')


def delete(request, narrative_id):
    narrative = get_object_or_404(Narrative, pk=narrative_id)
    experience = get_object_or_404(Experience, pk=narrative.experience_id)
    if request.method == 'POST' and 'confirm' in request.POST and narrative.author == request.user:
        narrative.delete()
        messages.success(request, 'Your narrative was deleted')
        return redirect('/experiences/{0}'.format(experience.id))
    else:
        return render(request, 'narratives/delete.html', {'narrative': narrative})


def upload_photo(request, narrative_id):
    narrative = get_object_or_404(Narrative, pk=narrative_id)
    if request.user == narrative.author:
        if narrative.gallery:
            gallery = narrative.gallery
        else:
            gallery = Gallery(title=narrative.title[:50], content_type=ContentType.objects.get(model='narrative'), object_pk=narrative.id, is_public=narrative.experience.is_public)
            gallery.save()
            gallery.explorers.add(request.user)
            narrative.gallery = gallery
            narrative.save()
        return redirect('/photologue/gallery/{0}/upload_photo/'.format(gallery.id))
    else:
        messages.error(request, 'Nice try on security breach! I would, however, love it if you did inform me of a website security weakness should (when) you find one.')
        return render(request, 'acressity/message.html')
