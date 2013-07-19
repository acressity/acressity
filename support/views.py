# All functions related to the relationship between an explorer and another object will be placed here. 

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.comments import Comment

from experiences.models import Experience


def track_experience(request, experience_id):
    if request.method == 'POST':
        experience = get_object_or_404(Experience, pk=experience_id)
        # Hmmm, really not sure if this is necessary. Might have been all along...
        if request.user.is_authenticated():
            # Keep explorer from tracking their own experiences
            # Perhaps this logic should be in the model manager save() method?
            if experience in request.user.experiences.all():
                messages.error(request, 'Sorry, you cannot track your own experiences')
            elif experience in request.user.tracking_experiences.all():
                messages.error(request, 'You are already tracking {0}'.format(experience))
            else:
                request.user.tracking_experiences.add(experience)
                messages.success(request, 'You are now tracking the experience {0}'.format(experience))
    return redirect(reverse('tracking_experiences', args=(request.user.id,)))


@login_required
def untrack_experience(request, experience_id):
    if request.method == 'POST':
        experience = get_object_or_404(Experience, pk=experience_id)
        if request.user.is_authenticated():
            if experience in request.user.tracking_experiences.all():
                request.user.tracking_experiences.remove(experience)
                messages.success(request, 'You are no longer tracking {0}'.format(experience))
            else:
                messages.error(request, 'You were not tracking that experience')
    return redirect(reverse('journey', args=(request.user.id,)))


@login_required
def remove_note(request, note_id):
    note = get_object_or_404(Comment, pk=note_id)
    if request.user == note.user:
        note.delete()
        messages.success(request, 'Note removed')
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        raise PermissionDenied
