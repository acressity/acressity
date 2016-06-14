from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth import get_user_model
from django.http import Http404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core.mail import send_mail
# from django.contrib.auth.decorators import login_required
from django.utils.html import escape
from django.views.generic import TemplateView
from django.template import RequestContext

from acressity import settings
from experiences.models import Experience, FeaturedExperience
from experiences.forms import ExperienceForm
from explorers.forms import RegistrationForm, Explorer
from acressity.forms import ContactForm
from paypal.standard.forms import PayPalPaymentsForm


def acressity_index(request):
    if request.user.is_authenticated():
        return redirect(reverse('journey', args=(request.user.id,)))
    else:
        return render(
            request, 'acressity/index.html',
            {
                'featured_experiences': FeaturedExperience.objects.get_random(3),
                'explorers': Explorer.objects.get_random(3)
            }
        )


def step_two(request):
    request.session['signing_up'] = 0
    if request.method == 'POST':
        exp_form = ExperienceForm(request.POST)
        if exp_form.is_valid():
            # Store the data in case they wish to peruse for a bit
            request.session['experience'] = exp_form.cleaned_data['experience']
            request.session['signing_up'] = 1
            reg_form = RegistrationForm()
            return render(
                request, 'registration/step_two.html',
                {
                    'experience': exp_form.cleaned_data['experience'],
                    'form': reg_form
                }
            )
    return redirect('/')
    return redirect(request.META['HTTP_REFERER'])


def handle_query_string(request, query_string):
    query_string = escape(query_string)
    if get_user_model().objects.filter(trailname=query_string):
        # Someone is requesting journey by trailname
        return redirect(
            reverse('journey', args=(get_user_model().objects.get(trailname=query_string).id,))
        )
    elif Experience.objects.filter(search_term=query_string):
        return redirect(
            reverse(
                'experience',
                args=(Experience.objects.get(search_term=query_string).id,))
        )
    else:
        raise Http404


def contact(request):
    # View handling the contact page
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            for admin in settings.ADMINS:
                send_mail(
                    'Message from {0} {1}'.format(
                        form.cleaned_data['first_name'],
                        form.cleaned_data['last_name']
                    ),
                    form.cleaned_data['message'] + '\n' +
                    form.cleaned_data['email'],
                    'acressity@acressity.com',
                    [admin[1]]
                )
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


def why(request):
    bike_across_america = Experience.objects.get(search_term='bike_across_america')
    bike_across_america_link = reverse('experience', args=(bike_across_america.id,))
    develop_this_website = Experience.objects.get(search_term='develop_this_website')
    develop_this_website_link = reverse('experience', args=(develop_this_website.id,))
    return render(request, 'acressity/why.html', {'bike_across_america_link':
        bike_across_america_link, 'develop_this_website_link':
        develop_this_website_link})


def example(request):
    bugsy = Explorer.objects.get(trailname='Bugsy')
    featured_explorer = Explorer.objects.get(pk=1)
    return render(request, 'acressity/example.html', {'bugsy': bugsy, 'featured_explorer': featured_explorer})


def handler404(request):
    response = render_to_response('acressity/404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('acressity/500.html', {}, context_instance=RequestContext(request))
    response.status_code = 500
    return response


def handler403(request):
    response = render_to_response('acressity/403.html', {}, context_instance=RequestContext(request))
    response.status_code = 403
    return response
