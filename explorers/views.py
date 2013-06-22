from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.comments import Comment
from django.contrib.auth import login, authenticate
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from django.contrib.auth import logout
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages

from explorers.forms import RegistrationForm, ExplorerForm
from explorers.models import Request
from experiences.models import Experience, FeaturedExperience
from photologue.models import Gallery, Photo
from experiences.forms import ExperienceForm
from narratives.models import Narrative
from support.models import Cheer


def journey(request, explorer_id):
    explorer = get_object_or_404(get_user_model(), pk=explorer_id)
    owner = explorer == request.user
    if owner:
        experiences = explorer.ordered_experiences()
    else:
        # Damn, this is hacky...
        # To start fixing this ugliness, must first have ordered_experiences() return a queryset instead of list
        experiences = []
        for experience in explorer.ordered_experiences():
            if experience.is_public:
                experiences += [experience]
            elif request.user.is_authenticated() and experience in request.user.experiences.all():
                experiences += [experience]
    return render(request, 'explorers/index.html', {'explorer': explorer, 'experiences': experiences, 'owner': owner})


@login_required
def my_journey(request):
    return redirect(reverse('journey', args=(request.user.id,)))


def story(request, explorer_id):
    explorer = get_object_or_404(get_user_model(), pk=explorer_id)
    if request.method == 'POST':
        if request.user == explorer:
            form = ExplorerForm(explorer, request.POST, instance=explorer)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your information has been saved')
            else:
                messages.error(request, 'There was a problem saving your information')
            return redirect('/explorers/{0}'.format(explorer.id))
        else:
            messages.error(request, 'Nice try on security breach! I would, however, love it if you did inform me of a website security weakness should (when) you find one.')
            return render(request, 'acressity/message.html')
    else:
        if request.user.id == explorer.id:
            owner = True
            form = ExplorerForm(explorer, instance=explorer)
        else:
            form = None
            owner = False
        return render(request, 'explorers/story.html', {'explorer': explorer, 'owner': owner, 'form': form})


def board(request, explorer_id):
    explorer = get_object_or_404(get_user_model(), pk=explorer_id)
    owner = explorer == request.user
    if owner:
        # Notes directly to the explorer
        eo_notes = Comment.objects.filter(content_type__model='explorer').filter(object_pk=explorer.id)
    else:
        eo_notes = []
    # Get the notes pertaining to all experiences
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
        if explorer == nr_note.content_object.author:
            nr_notes.append(nr_note)
    # Any requests pertaining to the explorer
    requests = Request.objects.filter(recruit=explorer)
    if request.method == 'POST' and request.user == explorer:
        invitation_request = requests.get(experience_id=request.POST.get('experience_id'))
        if 'accept' in request.POST:
            invitation_request.experience.explorers.add(explorer)
            invitation_request.experience.gallery.explorers.add(explorer)
            invitation_request.delete()
            return redirect(reverse('experiences.views.index', args=(invitation_request.experience.id,)))
        elif 'decline' in request.POST:
            invitation_request.delete()
    return render(request, 'explorers/bulletin_board.html', {'explorer': explorer, 'eo_notes': eo_notes, 'ei_notes': ei_notes, 'nr_notes': nr_notes, 'requests': requests, 'owner': owner})


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
            return redirect(reverse('journey', args=(explorer.id,)))
        else:
            messages.error(request, 'You are already cheering for {0}'.format(explorer.get_full_name()))
    return redirect(reverse('journey', args=(request.user.id,)))


# Those for whom the explorer is actively cheering
def cheering_for(request, explorer_id):
    explorer = get_object_or_404(get_user_model(), pk=explorer_id)
    return render(request, 'explorers/cheering_for.html', {'explorer': explorer})


def cheerers(request, explorer_id):
    explorer = get_object_or_404(get_user_model(), pk=explorer_id)
    return render(request, 'explorers/cheerers.html', {'explorer': explorer})


# This is to redirect user to their journey if the generic '/journey' url is called
@login_required
def explorer_journey(request):
    return redirect(reverse('journey', args=(request.user.id,)))


def new_explorer(request):
    if request.method == 'POST' and 'initial' not in request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # The person correctly filled out the form. Register them
            explorer = get_user_model()(trailname=form.cleaned_data['trailname'])
            explorer.set_password(form.cleaned_data['password1'])
            explorer.first_name = form.cleaned_data['first_name']
            explorer.last_name = form.cleaned_data['last_name']
            # explorer.email = form.cleaned_data['email']
            explorer.save()
            explorer = authenticate(username=form.cleaned_data['trailname'], password=form.cleaned_data['password1'])
            # Log them in
            login(request, explorer)
            if request.POST['experience']:
                # Save their experience
                first_experience = Experience(experience=request.POST['experience'], author=explorer)
                first_experience.save()
                explorer.experiences.add(first_experience)
                explorer.featured_experience = first_experience
                explorer.save()
                # messages.success(request, 'Your first experience is {0}'.format(first_experience))
            # Create a new gallery for the new explorer
            gallery = Gallery(title=explorer.trailname, title_slug=slugify(explorer.trailname), content_type=ContentType.objects.get(model='Explorer'), object_pk=explorer.id)
            gallery.save()
            gallery.explorers.add(explorer)
            explorer.gallery = gallery
            explorer.save()
            # Send them on introductory tour
            return redirect(reverse('welcome'))

            # Welcome the new explorer
            # messages.success(request, 'Go on, your journey awaits!')
    else:
        form = RegistrationForm()
    return render(request, 'acressity/register.html', {'form': form, 'experience': request.POST['experience']})


# Settings page for the explorer
@login_required
def settings(request, explorer_id):
    explorer = get_object_or_404(get_user_model(), pk=explorer_id)
    if request.user == explorer:
        return render(request, 'explorers/settings.html', {'explorer': explorer})


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
                # return HttpResponse(form.cleaned_data.__dict__)
                request.user.set_password(form.cleaned_data.get('new_password1'))  # For some reason unable to set to new_password2 because variable currently returning None. Kinda pissed/confused and wantig to move on...
                request.user.save()
                messages.success(request, 'You have successfully changed your password')
            else:
                messages.success(request, 'Your attempt to change your password failed...')
            return redirect(reverse('journey', args=(request.user.id,)))
    else:
        form = PasswordChangeForm
    return render(request, 'explorers/change_password.html', {'form': form})
