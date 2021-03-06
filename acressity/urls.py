from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib.auth.views import login

from acressity.views import WelcomeTemplateView

handler404 = 'acressity.views.handler404'
handler500 = 'acressity.views.handler500'
handler403 = 'acressity.views.handler403'

admin.autodiscover()

urlpatterns = patterns(
    'acressity.views',
    url(r'^$', 'acressity_index', name='acressity_index'),
    url(r'^explorers/', include('explorers.urls')),
    url(r'^experiences/', include('experiences.urls')),
    url(r'^narratives/', include('narratives.urls')),
    url(r'^photologue/', include('photologue.urls')),
    url(r'^support/', include('support.urls')),
    url(r'^comments/', include('django_comments_xtd.urls')),
    url(r'^why/$', 'why', name='why'),
    url(
        r'^what/$',
        TemplateView.as_view(template_name='acressity/what.html'),
        name='what'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^about/$', TemplateView.as_view(template_name='acressity/about.html'), name='about'),
    url(r'^step_two/', 'step_two', name="step_two"),
    url(r'^welcome/$', WelcomeTemplateView.as_view(), name='welcome'),
    url(
        r'^creators_note/$',
        TemplateView.as_view(template_name='acressity/creators_note.html'),
        name='creator_note'),
    url(
        r'^lexicon/$',
        TemplateView.as_view(template_name='acressity/lexicon.html'),
        name='lexicon'),
    url(r'^example/$', 'example', name='example'),
    # Patching to work with Django logout...
    url(r'^accounts/login/', login, name='login_page'),
    url(r'^contact/', 'contact', name='contact'),
    url(r'^notifications/', include('notifications.urls')),
    url(r'^paypal/', include('paypal.standard.ipn.urls')),
    # semi-primitive search for the query string provided.
    # Allows easier accessing of objects by an identifying string.
    # I believe this needs to remain at the bottom.
    url(r'^(?P<query_string>\w+)/$', 'handle_query_string', name='handle_query_string'),
)
