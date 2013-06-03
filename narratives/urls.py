from django.conf.urls import patterns, url

urlpatterns = patterns(
    'narratives.views',
    url(r'^$', 'index', name='experience_homepage'),
    url(r'^(?P<narrative_id>\d+)/$', 'index'),
    url(r'^create/$', 'create'),
    url(r'^edit/(?P<narrative_id>\d+)/$', 'edit'),
    url(r'^(?P<narrative_id>\d+)/delete/$', 'delete'),
    url(r'^(?P<narrative_id>\d+)/upload_photo/$', 'upload_photo'),
)
