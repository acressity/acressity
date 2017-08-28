from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView

from stripe_connect.views import (
    StripeAuthorize, StripeResponse, StripeDisconnect, StripePayment, 
    stripe_webhook, StripeAbout, 
)

urlpatterns = patterns(
    'stripe_connect.views',

    # Stripe payments
    url(
        r'^authorize/$',
        login_required(StripeAuthorize.as_view()),
        name='stripe_connect.authorize'
    ),
    url(
        r'^response/$',
        login_required(StripeResponse.as_view()),
        name='stripe_connect.response'
    ),
    url(
        r'^payment/bounty/(?P<pk>\d+)/$',
        StripePayment.as_view(),
        name='stripe_connect.bounty.payment'
    ),
    url(
        r'^webhook/$',
        stripe_webhook,
        name='stripe_connect.webhook'
    ),
    url(
        r'^disconnect/(?P<pk>\d+)/$',
        login_required(StripeDisconnect.as_view()),
        name='stripe_connect.disconnect'
    ),
    url(
        r'^about/$',
        StripeAbout.as_view(),
        name='stripe_connect.about'
    ),
)
