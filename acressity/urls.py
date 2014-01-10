from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib.auth.views import login

admin.autodiscover()

urlpatterns = patterns('acressity.views',
    url(r'^$', TemplateView.as_view(template_name='acressity/index.html'), name='acressity_index'),
    url(r'^explorers/', include('explorers.urls')),
    url(r'^experiences/', include('experiences.urls')),
    url(r'^narratives/', include('narratives.urls')),
    url(r'^photologue/', include('photologue.urls')),
    url(r'^support/', include('support.urls')),
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
    url(r'^contact/', 'contact', name='contact'),
    #('^notification/', include(notification.urls)),
    # ('^activity/', include('actstream.urls')),
    # semi-primitive search for the query string provided. Allows easier accessing of objects by an identifying string. Careful though: it matches any string not grabbed by the above. I believe this needs to remain at the bottom.
    url(r'^(?P<query_string>\w+)/$', 'handle_query_string', name='handle_query_string'),
)
