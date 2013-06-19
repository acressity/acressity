from django.conf.urls import patterns, url
from django.contrib.auth.views import login
from django.views.generic import ListView
from django.contrib.auth import get_user_model

urlpatterns = patterns(
    'explorers.views',
    url(r'^(?P<explorer_id>\d+)/$', 'journey', name='journey'),
    url(r'^journey/$', 'my_journey', name='my_journey'),
    url(r'^story/(?P<explorer_id>\d+)/$', 'story', name='story'),
    url(r'^login/$', login),
    url(r'^logout/$', 'farewell', name='farewell'),
    url(r'^journey/$', 'explorer_journey'),
    url(r'^new_explorer/$', 'new_explorer', name='register'),
    url(r'^(?P<explorer_id>\d+)/settings/$', 'settings'),
    url(r'^(?P<explorer_id>\d+)/board/$', 'board', name='board'),
    url(r'^random/$', 'random'),
    url(r'^all/$', ListView.as_view(queryset=get_user_model().objects.all(), context_object_name='all_explorers', template_name='explorers/all.html'), name="all_explorers"),
    url(r'^(?P<explorer_id>\d+)/cheer/$', 'cheer'),
    url(r'^(?P<explorer_id>\d+)/cheering_for/$', 'cheering_for'),
    url(r'^(?P<explorer_id>\d+)/cheerers/$', 'cheerers'),
    url(r'^change_password/$', 'change_password', name='change_password'),  # Private function, doesn't need explorer_id in url for others to see. More secure this way, hopefully
)
