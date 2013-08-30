# All functions related to the relationship between an explorer and another object will be placed here.
import random
import string

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
from support.models import InvitationRequest, PotentialExplorer
from support.forms import PotentialExplorerForm
from explorers.forms import RegistrationForm


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
        # Poohbear is a honeypot input element. Used to catch scripts filling every form input. Hidden from interface
        poohbear = request.POST.get('poohbear')
        if len(comment) >= 5:
            message = comment + '\n\n{0}'.format(request.META.get('HTTP_REFERER'))
            if poohbear:
                message += '\n\nAnd a poohbear: {0}'.format(poohbear)
            send_mail('Comments from Acressity', message, 'acressity@acressity.com', ['andrew.s.gaines@gmail.com'])
            messages.success(request, 'Thank you for your comment! It will be used to improve the site.')
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def accept_invitation_request(request, explorer_id, invitation_request_id):
    explorer = get_object_or_404(get_user_model(), pk=explorer_id)
    invitation_request = get_object_or_404(InvitationRequest, pk=invitation_request_id)
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
    invitation_request = get_object_or_404(InvitationRequest, pk=invitation_request_id)
    if request.user == explorer:
        messages.success(request, 'You have declined the invitation to the experience {0}.'.format(invitation_request.experience))
        invitation_request.delete()
        return redirect(request.META.get('HTTP_REFERER'))


def experience_invite(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.user != experience.author:
        messages.error(request, 'Sorry, you do not have the ability of inviting others to this experience')
        return render(request, 'acressity/message.html')
    explorers = get_user_model().objects.exclude(experiences=experience).exclude(experience_recruit__experience=experience)  # Remove those who are already a part of the experience and those who have an outstanding request
    if request.method == 'POST':
        if 'existing_explorer' in request.POST:
            recruit = get_user_model().objects.get(pk=int(request.POST.get('explorer_id')))
            experience_request = InvitationRequest(author=request.user, recruit=recruit, experience=experience)
            experience_request.save()
            messages.success(request, 'You have invited {0} to be a part of {1}.'.format(recruit.get_full_name(), experience))
            return redirect(reverse('experience_invite', args=(experience.id,)))
        elif 'email' in request.POST:
            form = PotentialExplorerForm(request.POST)
            if form.is_valid():
                form.save()
                invitation_request = InvitationRequest(author=request.user, potential_explorer=form.instance, experience=experience, code=''.join([random.choice(string.ascii_letters + string.digits) for i in range(25)]))
                invitation_request.save()
                send_mail(
                    'Invitation from {0}'.format(request.user.get_full_name()), 'Hello {3} {4},\nYou\'ve been invited by {0} to participate in the experience "{1}"\n\nTo view this invitation, go to http://acressity.com/support/view_invitation/{2}\n\nIf you do not know this person, or believe this email was sent in error, please ignore or respond to acressity@acressity.com'.format(request.user.get_full_name(), experience, invitation_request.code, form.instance.first_name, form.instance.last_name), 'acressity@acressity.com', [form.cleaned_data['email']])
                messages.success(request, 'You have successfully invited {0} {1}'.format(form.cleaned_data['first_name'], form.cleaned_data['last_name']))
                return redirect(reverse('experience', args=(experience.id,)))
    else:
        form = PotentialExplorerForm()
    return render(request, 'support/experience_invite.html', {'experience': experience, 'explorers': explorers, 'form': form})


def view_invitation(request, code):
    invitation_request = get_object_or_404(InvitationRequest, code=code)
    if request.method == 'POST':
        if 'accept' in request.POST:
            # With the current implementation, this will never be called. The accept form is directing straight to the register view in explorers app. Don't know how to redirect from here with the valuable POST data still intact from the PotentialExplorer object...
            return redirect(reverse('register'), request=request)
        elif 'decline' in request.POST:
            # Rejected... Clean up the garbage
            invitation_request.potential_explorer.delete()
            invitation_request.delete()
            messages.success(request, 'You have declined the invitation')
            return redirect(reverse('acressity_index'))
    return render(request, 'support/view_invitation.html', {'invitation_request': invitation_request})
