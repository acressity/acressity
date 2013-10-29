from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.http import Http404
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.utils.html import escape

from experiences.models import Experience, FeaturedExperience
from experiences.forms import ExperienceForm
from explorers.forms import RegistrationForm
from acressity.forms import ContactForm


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


def handle_query_string(request, query_string):
    query_string = escape(query_string)
    if get_user_model().objects.filter(trailname=query_string):
        # Someone is requesting journey by trailname
        return redirect(reverse('journey', args=(get_user_model().objects.get(trailname=query_string).id,)))
    elif Experience.objects.filter(search_term=query_string):
        return redirect(reverse('experience', args=(Experience.objects.get(search_term=query_string).id,)))
    else:
        raise Http404


def contact(request):
    # View handling the contact page
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            send_mail('Message from {0} {1}'.format(form.cleaned_data['first_name'], form.cleaned_data['last_name']), form.cleaned_data['message'], 'acressity@acressity.com', ['andrew.s.gaines@gmail.com'])
            messages.success(request, 'Thank you for your message')
            return redirect(reverse('contact'))
    else:
        form = ContactForm()
    return render(request, 'acressity/contact.html', {'form': form})
