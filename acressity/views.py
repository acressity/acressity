from experiences.models import Experience, FeaturedExperience
from experiences.forms import ExperienceForm
from explorers.forms import RegistrationForm

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def index(request):
    explorer_experience = []
    featured_experiences = FeaturedExperience.objects.get_random(5)
    for featured_experience in featured_experiences:
        explorer = get_user_model().objects.get(pk=featured_experience.experience.author_id)
        explorer_experience.append((explorer, featured_experience.experience))
    # Form for experience
    form = ExperienceForm()
    return render(request, 'acressity/index.html', {'form': form, 'explorer_experience': explorer_experience})


def step_two(request):
    # Following is kinda hacky because of an unnecessary redirect, but okay for now....though it hurts my soul just a lil' bit
    if not request.POST.get('experience'):
        # User chose to create profile without initial experience
        return redirect(reverse('register'))
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            experience = form.cleaned_data['experience']
            form = RegistrationForm()
            return render(request, 'registration/step_two.html', {'experience': experience, 'form': form})


def journey_by_trailname(request, trailname):
    # Pathetically primitive search algorithm...of sorts
    explorer = get_object_or_404(get_user_model(), trailname=trailname)
    return redirect(reverse('journey', args=(explorer.id,)))
