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
    # Private functions, doesn't need explorer_id in url for others to see. More secure this way, I believe
    url(r'^change_password/$', 'change_password', name='change_password'),
)

urlpatterns += patterns(
    '',
    url(r'^reset_password/$', 'django.contrib.auth.views.password_reset', {'post_reset_redirect': '/explorers/reset_password/done/'},
        name="reset_password"),
    url(r'^reset_password/done/$',
        'django.contrib.auth.views.password_reset_done'),
    url(r'^reset_password/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'post_reset_redirect': '/explorers/password/done/'}),
    url(r'^password/done/$', 'django.contrib.auth.views.password_reset_complete'),
)
