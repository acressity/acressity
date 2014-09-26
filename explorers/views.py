import simplejson

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.comments import Comment
from django.contrib.auth import login, authenticate
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from django.contrib.auth import logout
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.conf import settings

from explorers.forms import RegistrationForm, ExplorerForm
from support.models import InvitationRequest
from notifications import notify
from experiences.models import Experience, FeaturedExperience
from photologue.models import Gallery, Photo
from experiences.forms import ExperienceForm
from narratives.models import Narrative
from support.models import Cheer


def journey(request, explorer_id):
    explorer = get_object_or_404(get_user_model(), pk=explorer_id)
    owner = explorer == request.user
    form = None
    if owner:
        experiences = explorer.ordered_experiences()
        form = ExperienceForm()
    else:
        # Damn, this is hacky...
        # To start fixing this ugliness, must first have ordered_experiences() return a queryset instead of list
        experiences = []
        for experience in explorer.ordered_experiences():
            if experience.is_public:
                experiences += [experience]
            elif request.user.is_authenticated() and experience in request.user.experiences.all():
                experiences += [experience]
    return render(request, 'explorers/index.html', {'explorer': explorer, 'experiences': experiences, 'owner': owner, 'form': form})


@login_required
def my_journey(request):
    return redirect(reverse('journey', args=(request.user.id,)))


def profile(request, explorer_id):
    explorer = get_object_or_404(get_user_model(), pk=explorer_id)
    if request.method == 'POST':
        if request.user == explorer:
            form = ExplorerForm(explorer, request.POST, instance=explorer)
            if form.is_valid():
                form.save()
                messages.success(request, _('Your information has been saved'))
            # else:
            #     messages.error(request, 'There was a problem saving your information')
            # return redirect('/explorers/{0}'.format(explorer.id))
        else:
            messages.error(request, _('Nice try on security breach! I would, however, love it if you did inform me of a website security weakness should (when) you find one.'))
            return render(request, 'acressity/message.html')
    if request.user.id == explorer.id:
        owner = True
        form = ExplorerForm(explorer, instance=explorer)
    else:
        form = None
        owner = False
    return render(request, 'explorers/profile.html', {'explorer': explorer, 'owner': owner, 'form': form})


def story(request, explorer_id):
    explorer = get_object_or_404(get_user_model(), pk=explorer_id)
    if request.user == explorer:
        narratives = explorer.narratives.all()
    else:
        narratives = explorer.narratives.filter(is_public=True)
    return render(request, 'explorers/story.html', {'narratives': narratives})


def board(request, explorer_id):
    explorer = get_object_or_404(get_user_model(), pk=explorer_id)
    owner = explorer == request.user
    if owner:
        # Notes directly to the explorer
        eo_notes = Comment.objects.filter(content_type__model='explorer').filter(object_pk=explorer.id)
    else:
        eo_notes = []
    # Get the notes pertaining to all experiences
    # What was I thinking? This will become about the most inefficient thing imagineable as (if) more experiences notes are added
    experience_notes = Comment.objects.filter(content_type__model='experience')
    # Filter the results down for just the experiences pertaining to explorer
    ei_notes = []
    for ei_note in experience_notes:
        if explorer in ei_note.content_object.explorers.all():
            ei_notes.append(ei_note)
    # Get the notes queryset pertaining to all narratives
    narrative_notes = Comment.objects.filter(content_type__model='narrative')
    # Filter the results down for just the experiences pertaining to explorer
    nr_notes = []
    for nr_note in narrative_notes:
        if nr_note.content_object:
            if explorer == nr_note.content_object.author:
                nr_notes.append(nr_note)
    # Any requests pertaining to the explorer
    requests = InvitationRequest.objects.filter(recruit=explorer)
    if request.method == 'POST' and request.user == explorer:
        invitation_request_id = request.POST.get('invitation_request_id')
        if 'accept' in request.POST:
            return redirect(reverse('accept_invitation_request', args=(request.user.id,)))
        elif 'decline' in request.POST:
            return redirect(reverse('decline_invitation_request', args=(request.user.id, invitation_request_id)))
    nothing = not (ei_notes or nr_notes or requests)
    notifications = explorer.notifications.unread()
    return render(request, 'explorers/bulletin_board.html', {'explorer': explorer, 'eo_notes': eo_notes, 'ei_notes': ei_notes, 'nr_notes': nr_notes, 'requests': requests, 'nothing': nothing, 'owner': owner, 'notifications': notifications})


@login_required
def past_notifications(request, explorer_id):
    return render(request, 'explorers/past_notifications.html')


# For subscription relationships
@login_required
def cheer(request, explorer_id):
    if request.method == 'POST':
        explorer = get_object_or_404(get_user_model(), pk=explorer_id)
        explorer_cheerers = [c.cheerer for c in explorer.cheers_for.all()]
        if request.user not in explorer_cheerers and request.user is not explorer:
            cheer = Cheer(explorer=explorer, cheerer=request.user)
            cheer.save()
            messages.success(request, 'You are now cheering for {0}'.format(explorer.get_full_name()))
            notify.send(sender=request.user, recipient=explorer, verb='is now cheering for you')
            return redirect(reverse('journey', args=(explorer.id,)))
        else:
            messages.error(request, _('You are already cheering for {0}'.format(explorer.get_full_name())))
    return redirect(reverse('journey', args=(request.user.id,)))


# Those for whom the explorer is actively cheering
def cheering_for(request, explorer_id):
    explorer = get_object_or_404(get_user_model(), pk=explorer_id)
    return render(request, 'explorers/cheering_for.html', {'explorer': explorer})


def cheerers(request, explorer_id):
    explorer = get_object_or_404(get_user_model(), pk=explorer_id)
    return render(request, 'explorers/cheerers.html', {'explorer': explorer})


# I'm going to get a generic view serving this sometime...
def tracking_experiences(request, explorer_id):
    tracking_experiences = request.user.tracking_experiences.all()
    return render(request, 'explorers/tracking_experiences.html', {'tracking_experiences': tracking_experiences})


# This is to redirect user to their journey if the generic '/journey' url is called
@login_required
def explorer_journey(request):
    return redirect(reverse('journey', args=(request.user.id,)))


def new_explorer(request):
    if request.method == 'POST' and 'initial' not in request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # The person correctly filled out the form. Register them
            explorer = get_user_model()(email=form.cleaned_data.get('email'))
            explorer.set_password(form.cleaned_data['password1'])
            explorer.first_name = form.cleaned_data['first_name']
            explorer.last_name = form.cleaned_data['last_name']
            # explorer.email = form.cleaned_data['email']
            explorer.save()
            explorer = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            # Log them in
            login(request, explorer)
            if request.POST.get('experience'):
                # Save their experience
                first_experience = Experience(experience=request.POST.get('experience'), author=explorer)
                first_experience.save()
                explorer.experiences.add(first_experience)
                explorer.featured_experience = first_experience
                explorer.save()
            # Create a new gallery for the new explorer
            gallery = Gallery(title=explorer.get_full_name(), title_slug=slugify(explorer.trailname), content_type=ContentType.objects.get(model='Explorer'), object_pk=explorer.id)
            gallery.save()
            gallery.explorers.add(explorer)
            explorer.gallery = gallery
            explorer.save()
            # Welcome and send them on introductory tour?
            messages.success(request, 'Welcome aboard, {0}'.format(explorer.get_full_name()))
            notify.send(sender=explorer, recipient=get_user_model().objects.get(pk=1), verb='is now a fellow explorer')
            return redirect(reverse('journey', args=(explorer.id,)))
        # else:
        #     messages.error(request, 'Please provide an experience you wish to have')
        #     return redirect(request.META.get('HTTP_REFERER'))
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form, 'experience': request.POST.get('experience'), 'min_password_len': settings.MIN_PASSWORD_LEN})


# Settings page for the explorer
@login_required
def explorer_settings(request, explorer_id):
    explorer = get_object_or_404(get_user_model(), pk=explorer_id)
    if request.user == explorer:
        return render(request, 'explorers/explorer_settings.html', {'explorer': explorer})


def random(request):
    random_explorers = get_user_model().objects.order_by('?')[:5]
    return render(request, 'explorers/random.html', {'random_explorers': random_explorers})


@login_required
def farewell(request):
    featured_experience = request.user.featured_experience
    logout(request)
    return render(request, 'explorers/farewell.html', {'featured_experience': featured_experience})


@login_required
def change_password(request):
    from explorers.forms import PasswordChangeForm
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST, request=request)
        if form.is_valid():
            if request.user.check_password(form.cleaned_data.get('current_password')):
                request.user.set_password(form.cleaned_data.get('new_password1'))  # For some reason unable to set to new_password2 because variable currently returning None. Kinda pissed/confused and wanting to move on...
                request.user.save()
                messages.success(request, _('You have successfully changed your password'))
            else:
                messages.success(request, _('Your attempt to change your password failed...'))
            return redirect(reverse('journey', args=(request.user.id,)))
    else:
        form = PasswordChangeForm
    return render(request, 'explorers/change_password.html', {'form': form})


def site_login(request):
    if request.GET.get('next') == '/explorers/logout/' or request.POST.get('next') == '/explorers/logout/' or request.META.get('HTTP_REFERER') == request.build_absolute_uri(reverse('acressity_index')):
        next_url = reverse('my_journey')
    else:
        next_url = request.GET.get('next') or request.POST.get('next') or 'my_journey'
    username_provided = request.POST.get('username')
    if username_provided is None:
        messages.error(request, _('Please provide either your email or optional trailname for logging in'))
        return redirect('/accounts/login')
    password_provided = request.POST.get('password')
    # Site allows one to login with either email address or created trailname
    if get_user_model().objects.filter(email=username_provided):
        explorer = authenticate(username=username_provided, password=password_provided)
        if explorer:
            login(request, explorer)
            return redirect(next_url)
    if get_user_model().objects.filter(trailname=username_provided):
        explorer = get_user_model().objects.get(trailname=username_provided)
        explorer = authenticate(username=explorer.email, password=password_provided)
        if explorer:
            login(request, explorer)
            # return HttpResponse(next_url)
            return redirect(next_url)
    # Login failed
    messages.error(request, _('There was a problem with your username or password'))
    return redirect('/accounts/login')


def check_trailname(request):
    trailname = request.GET.get('trailname')
    return HttpResponse(simplejson.dumps({'found': bool(get_user_model().objects.filter(trailname=trailname))}), mimetype='application/json')
