from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib.auth.views import login

from acressity.views import journey, journey_by_trailname
admin.autodiscover()

urlpatterns = patterns(
    'acressity.views',
    # url matches id of user, calls journey view, now deprecated!!
    url(r'^(?P<explorer_id>\d+)/$', journey),
    # url(r'^journey/$', 'acressity.views.my_journey', name='my_journey'),
    url(r'^explorers/', include('explorers.urls')),
    url(r'^experiences/', include('experiences.urls')),
    url(r'^narratives/', include('narratives.urls')),
    url(r'^$', 'index'),
    url(r'^photologue/', include('photologue.urls')),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^about/$', TemplateView.as_view(template_name='acressity/about.html'), name='about'),
    url(r'^step_two/', 'step_two', name="step_two"),
    url(r'^welcome/$', TemplateView.as_view(template_name='acressity/welcome.html'), name='welcome'),
    url(r'^creator_note/$', TemplateView.as_view(template_name='acressity/creator_note.html'), name='creator_note'),
    url(r'^glossary/$', TemplateView.as_view(template_name='acressity/glossary.html'), name='glossary'),
    # Patching to work with Django logout...
    url(r'^accounts/login/', login),
    # url matching a string, calling view which checks if == trailname (nickname), and returns the url for the matching explorer_id
    url(r'^(?P<trailname>\w+)/$', journey_by_trailname),
)
