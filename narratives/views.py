from datetime import datetime
from itertools import chain
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

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
            if not request.user.is_authenticated():
                # Non-logged in user might be author/comrade. Give them chance
                # to log in
                return redirect(settings.LOGIN_URL + '?next=' + request.path)
            else:
                # This user simply does not have the privileges
                raise PermissionDenied
    return render(request, 'narratives/index.html', {'narrative': narrative, 'privileged': privileged, 'author': narrative.is_author(request)})


@login_required
def create(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == 'POST' and experience.is_comrade(request):
        form = NarrativeForm(request.POST, author=request.user)
        if form.is_valid():
            new_narrative = form.save()
            messages.success(request, 'Your narrative has been added')
            for explorer in set(chain(experience.comrades(request), experience.tracking_explorers.all())):
                notify.send(recipient=explorer, sender=request.user, target=new_narrative, verb='has written a new narrative for experience {0}'.format(experience))
            return redirect('/narratives/{0}'.format(new_narrative.id))
    else:
        narr_form_context = {'experience': experience.id, 'is_public':
                experience.is_public, 'title': datetime.now().strftime('%B %d, %Y')}
        form = NarrativeForm(author=request.user, initial=narr_form_context)
    return render(request, 'narratives/create.html', {'form': form, 'experience': experience})


# Following for AJAX saving purposes. Replace edit??
@login_required
def save(request, narrative_id):
    json = json.dumps({'success': 'no post'})
    return HttpResponse(json)


@login_required
def edit(request, narrative_id):
    narrative = get_object_or_404(Narrative, pk=narrative_id)
    if narrative.author == request.user:
        if request.method == 'POST':
            form = NarrativeForm(request.POST, author=narrative.author, instance=narrative)
            if form.is_valid():
                form.save()
                messages.success(request, 'Narrative successfully updated')
                for explorer in narrative.experience.comrades(request):
                    notify.send(recipient=explorer, sender=request.user, target=narrative, verb='edited a narrative')
                return redirect('/narratives/{0}'.format(narrative.id))
        else:
            form = NarrativeForm(author=narrative.author, instance=narrative)
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
            gallery = Gallery(title=narrative.title[:50], content_type=ContentType.objects.get_for_model(Narrative), object_pk=narrative.id, is_public=narrative.experience.is_public)
            gallery.save()
            gallery.explorers.add(request.user)
            narrative.gallery = gallery
            narrative.save()
        return redirect('/photologue/gallery/{0}/upload_photo/'.format(gallery.id))
    raise PermissionDenied


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
