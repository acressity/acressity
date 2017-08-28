from django.conf.urls import patterns, url

urlpatterns = patterns(
    'support.views',
    url(r'^track_experience/(?P<experience_id>\d+)/$', 'track_experience', name='track_experience'),
    url(r'^untrack_experience/(?P<experience_id>\d+)/$', 'untrack_experience', name='untrack_experience'),
    url(r'^remove_note/(?P<note_id>\d+)/$', 'remove_note', name='remove_note'),
    url(r'^comment_to_creator/$', 'comment_to_creator', name='comment_to_creator'),
    url(r'^experience_invite/(?P<experience_id>\d+)/$', 'experience_invite', name='experience_invite'),
    url(r'^view_invitation/(?P<code>\w{25})/$', 'view_invitation', name='view_invitation'),
    url(r'^handle_invitation_request/(?P<invitation_request_id>\d+)/$', 'handle_invitation_request', name='handle_invitation_request'),
    url(r'^experience/(?P<experience_id>\d+)/donate/$', 'donate', name='donate'),
    url(r'^experience/(?P<experience_id>\d+)/paypal_return/$', 'paypal_return', name='paypal_return'),
)
