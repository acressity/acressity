from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.http import Http404
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core.mail import send_mail
# from django.contrib.auth.decorators import login_required
from django.utils.html import escape
from django.views.generic import TemplateView

from experiences.models import Experience, FeaturedExperience
from experiences.forms import ExperienceForm
from explorers.forms import RegistrationForm, Explorer
from acressity.forms import ContactForm


def acressity_index(request):
    if request.user.is_authenticated():
        return redirect(reverse('journey', args=(request.user.id,)))
    else:
        return render(request, 'acressity/index.html', {'featured_experiences': FeaturedExperience.objects.get_random(3), 'explorers': Explorer.objects.get_random(3)})


def step_two(request):
    request.session['signing_up'] = 0
    if request.method == 'POST':
        exp_form = ExperienceForm(request.POST)
        if exp_form.is_valid():
            request.session['experience'] = exp_form.cleaned_data['experience']  # Store the data in case they wish to peruse for a bit
            request.session['signing_up'] = 1
            reg_form = RegistrationForm()
            return render(request, 'registration/step_two.html', {'experience': exp_form.cleaned_data['experience'], 'form': reg_form})
    return redirect('/')
    return redirect(request.META['HTTP_REFERER'])


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


class WelcomeTemplateView(TemplateView):
    template_name = 'registration/welcome.html'

    def get_context_data(self, **kwargs):
        context = super(WelcomeTemplateView, self).get_context_data(**kwargs)
        context['form'] = ExperienceForm()
        return context
