from django.conf.urls import patterns, url
from django.views.generic import ListView
from narratives.models import Narrative

urlpatterns = patterns(
    'narratives.views',
    url(r'^$', ListView.as_view(queryset=Narrative.objects.exclude(is_public=False), context_object_name='all_public_narratives', template_name='narratives/all.html', paginate_by=10), name='narrative_homepage'),
    url(r'^(?P<narrative_id>\d+)/$', 'index', name='narrative'),
    url(r'^create/$', 'create', name='create_narrative'),
    url(r'^edit/(?P<narrative_id>\d+)/$', 'edit'),
    url(r'^(?P<narrative_id>\d+)/delete/$', 'delete'),
    url(r'^(?P<narrative_id>\d+)/upload_photo/$', 'upload_photo'),
    url(r'^all/(?P<explorer_id>\d+)/$', 'all', name='all_explorer_narratives'),
    url(r'^(?P<narrative_id>\d+)/save/$', 'save', name='save'),
)
