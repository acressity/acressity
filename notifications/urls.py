from django.conf.urls import *

urlpatterns = patterns('notifications.views',
    url(r'^$', 'all', name='all'),
    url(r'^unread/$', 'unread', name='unread'),
    url(r'^mark-all-as-read/$', 'mark_all_as_read', name='mark_all_as_read'),
    url(r'^mark-as-read/(?P<notice_id>\d+)/$', 'mark_as_read', name='mark_as_read'),
    url(r'^mark-as-unread/(?P<notice_id>\d+)/$', 'mark_as_unread', name='mark_as_unread'),
)
