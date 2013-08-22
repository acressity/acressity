# All functions related to the relationship between an explorer and another object will be placed here.

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied
from django.contrib.comments import Comment
from django.contrib.auth import get_user_model
from django.http import HttpResponse

from experiences.models import Experience
from support.models import Request


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


def comment_to_creator(request):
    if request.method == 'POST':
        comment = request.POST.get('comment_to_creator')
        poohbear = request.POST.get('poohbear')
        if len(comment) >= 5:
            message = comment + '\n\n{0}'.format(request.META.get('HTTP_REFERER'))
            if poohbear:
                message += '\n\nAnd a poohbear: {0}'.format(poohbear)
            send_mail('Comments from Users', message, 'acressity@acressity.com', ['andrew.s.gaines@gmail.com'])
            messages.success(request, 'Thank you for your comment! It will be used to improve the site.')
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def accept_invitation_request(request, explorer_id, invitation_request_id):
    explorer = get_object_or_404(get_user_model(), pk=explorer_id)
    invitation_request = get_object_or_404(Request, pk=invitation_request_id)
    if request.user == explorer:
        invitation_request.experience.explorers.add(explorer)
        if invitation_request.experience.gallery:
            invitation_request.experience.gallery.explorers.add(explorer)
        messages.success(request, 'You are now an explorer of {0}. You can edit aspects of the experience, upload narratives, and add your own photos. Enjoy!'.format(invitation_request.experience))
        invitation_request.delete()
        return redirect(reverse('experiences.views.index', args=(invitation_request.experience.id,)))


@login_required
def decline_invitation_request(request, explorer_id, invitation_request_id):
    explorer = get_object_or_404(get_user_model(), pk=explorer_id)
    invitation_request = get_object_or_404(Request, pk=invitation_request_id)
    if request.user == explorer:
        messages.success(request, 'You have declined the invitation to the experience {0}.'.format(invitation_request.experience))
        invitation_request.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    
        
