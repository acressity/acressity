from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils import simplejson
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from narratives.models import Narrative
from narratives.forms import NarrativeForm
from experiences.models import Experience
from photologue.models import Gallery
from notifications import notify


def index(request, narrative_id):
    narrative = get_object_or_404(Narrative, pk=narrative_id)
    privileged = request.user in narrative.experience.explorers.all()
    if not privileged:
        if request.get_signed_cookie('experience_password', salt='personal_domain', default=False):
            if request.get_signed_cookie('experience_password', salt='personal_domain') == str(narrative.experience.id):
                privileged = True
    if not privileged and (not narrative.is_public or not narrative.experience.is_public):
        if narrative.experience.password:
            return redirect(reverse('check_password', args=(narrative.experience.id,)))
        else:
            raise PermissionDenied
    return render(request, 'narratives/index.html', {'narrative': narrative, 'privileged': privileged, 'author': narrative.is_author(request)})


@login_required
def create(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == 'POST' and experience.is_comrade(request):
        form = NarrativeForm(request.user, request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.instance.author = request.user
            new_narrative = form.save()
            messages.success(request, 'Your narrative has been added')
            for comrade in experience.comrades(request):
                notify.send(recipient=comrade, sender=request.user, target=new_narrative, verb='has written a new narrative for experience {0}'.format(experience))
            return redirect('/narratives/{0}'.format(new_narrative.id))
    else:
        form = NarrativeForm(request.user, initial={'experience': experience.id, 'is_public': experience.is_public})
    return render(request, 'narratives/create.html', {'form': form, 'experience': experience})


# Following for AJAX saving purposes. Replace edit??
@login_required
def save(request, narrative_id):
    json = simplejson.dumps({'success': 'no post'})
    return HttpResponse(json)


@login_required
def edit(request, narrative_id):
    narrative = get_object_or_404(Narrative, pk=narrative_id)
    if narrative.author == request.user:
        if request.method == 'POST':
            form = NarrativeForm(narrative.author, request.POST, instance=narrative)
            if form.is_valid():
                form.save()
                messages.success(request, 'Narrative successfully updated')
                for comrade in narrative.experience.comrades(request):
                    notify.send(recipient=comrade, sender=request.user, target=narrative, verb='edited a narrative')
                return redirect('/narratives/{0}'.format(narrative.id))
        else:
            form = NarrativeForm(narrative.author, instance=narrative)
        return render(request, 'narratives/edit.html', {'form': form, 'narrative': narrative})
    else:
        raise PermissionDenied


@login_required
def delete(request, narrative_id):
    narrative = get_object_or_404(Narrative, pk=narrative_id)
    if request.method == 'POST' and 'confirm' in request.POST and narrative.author == request.user:
        narrative.delete()
        messages.success(request, 'Your narrative was deleted')
        for comrade in narrative.experience.comrades(request):
            notify.send(sender=request.user, recipient=comrade, verb='has deleted a narrative from the experience', target=narrative.experience)
        return redirect(reverse('experience', args=(narrative.experience.id,)))
    else:
        return render(request, 'narratives/delete.html', {'narrative': narrative})


@login_required
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


def all(request, explorer_id):
    explorer = get_object_or_404(get_user_model(), pk=explorer_id)
    narrative_queryset = explorer.narratives.order_by('-date_created')
    if request.user == explorer:
        narrative_set = narrative_queryset
    else:
        narrative_set = narrative_queryset.filter(is_public=True)
    paginator = Paginator(narrative_set, 10)
    page = request.GET.get('page')
    try:
        narratives = paginator.page(page)
    except PageNotAnInteger:
        # Deliver the first page
        narratives = paginator.page(1)
    except EmptyPage:
        # Deliver last page
        narratives = paginator.page(paginator.num_pages)
    return render(request, 'narratives/all_explorer_narratives.html', {'explorer': explorer, 'page_obj': narratives, 'is_paginated': True})
