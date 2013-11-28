from django.conf.urls import patterns, url, include
from django.views.generic import ListView
from experiences.models import Experience

urlpatterns = patterns(
    'experiences.views',
    url(r'^$', 'home'),
    url(r'^(?P<experience_id>\d+)/$', 'index', name="experience"),
    url(r'^edit/(?P<experience_id>\d+)/$', 'edit', name='edit_experience'),
    url(r'^create/$', 'create', name='create_experience'),
    url(r'^(?P<experience_id>\d+)/delete/$', 'delete', name='delete_experience'),
    url(r'^(?P<experience_id>\d+)/brief/$', 'brief'),
    url(r'^(?P<experience_id>\d+)/categorize/$', 'categorize'),
    url(r'^freshest/$', ListView.as_view(queryset=Experience.objects.exclude(is_public=False).order_by('date_created')[:5], context_object_name='freshest_experiences', template_name='experiences/freshest.html'), name="freshest_experiences"),
    url(r'^featured/$', 'featured', name='featured_experiences'),
    url(r'^(?P<experience_id>\d+)/narratives/', include('narratives.urls')),
    url(r'^(?P<experience_id>\d+)/gallery/$', 'gallery', name='exp-gallery-list'),
    url(r'^(?P<experience_id>\d+)/upload_photo/$', 'upload_photo'),
    url(r'^(?P<experience_id>\d+)/check_password/$', 'check_password', name='check_password'),
    url(r'^all/$', ListView.as_view(queryset=Experience.objects.exclude(is_public=False), context_object_name='all_public_experiences', template_name='experiences/all.html'), name="all_experiences"),
    url(r'^create_experience/$', 'create', name='create_experience'),
    url(r'^(?P<experience_id>\d+)/leave_experience/$', 'leave_experience', name='leave_experience'),
)
