from django.conf.urls import patterns, url, include
from django.views.generic import ListView

from experiences.models import Experience

urlpatterns = patterns(
    'experiences.views',
    url(r'^$',
        ListView.as_view(
            queryset=Experience.objects.exclude(is_public=False),
            context_object_name='all_public_experiences',
            template_name='experiences/all.html', paginate_by=10
        ), name="all_experiences"),
    url(r'^(?P<experience_id>\d+)/$', 'index', name="experience"),
    url(r'^edit/(?P<experience_id>\d+)/$', 'edit', name='edit_experience'),
    url(r'^create/$', 'create', name='create_experience'),
    url(r'^(?P<experience_id>\d+)/delete/$', 'delete', name='delete_experience'),
    url(r'^(?P<experience_id>\d+)/brief/$', 'brief', name='experience_brief'),
    url(r'^(?P<experience_id>\d+)/categorize/$', 'categorize'),
    url(r'^freshest/$',
        ListView.as_view(
            queryset=Experience.objects.exclude(is_public=False).order_by('-date_created'),
            context_object_name='freshest_experiences',
            template_name='experiences/freshest.html', paginate_by=10
        ), name="freshest_experiences"),
    url(r'^random/$',
        ListView.as_view(
            queryset=Experience.objects.exclude(is_public=False).order_by('?'),
            context_object_name='random_experiences',
            template_name='experiences/random.html'
        ), name="random_experiences"),
    url(r'^featured/$', 'featured', name='featured_experiences'),
    url(r'^(?P<experience_id>\d+)/narratives/', include('narratives.urls')),
    url(r'^(?P<experience_id>\d+)/gallery/$', 'gallery', name='exp-gallery-list'),
    url(r'^(?P<experience_id>\d+)/upload_photo/$', 'upload_photo', name='exp_upload_photo'),
    url(r'^(?P<experience_id>\d+)/check_password/$',
        'check_password', name='experience_check_password'
        ),
    url(r'^(?P<experience_id>\d+)/leave_experience/$', 'leave_experience', name='leave_experience'),
    url(r'^(?P<experience_id>\d+)/new_experience/$', 'new_experience', name='new_experience'),
    url(r'^(?P<experience_id>\d+)/donate/$', 'donate', name='donate'),
    url(r'^(?P<experience_id>\d+)/paypal_return/$', 'paypal_return', name='paypal_return'),
    url(r'^ajax_thing/$', 'ajax_thing'),
    url(r'^(?P<experience_id>\d+)/transfer_narratives/$', 'transfer_narratives', name='transfer_narratives'),
)
