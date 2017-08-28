from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from benefaction.views import (
    CampaignIndex, CampaignCreate, CampaignEdit, CampaignDelete, 
    CampaignPaidBountiesListView, CampaignFulfilledBountiesListView,
    BountyIndex, BountyCreate, BountyEdit, BountyDelete, BountyAccept, 
    BountyCancelAccept
)
from benefaction.models import Campaign, Bounty

urlpatterns = patterns(
    'benefaction.views',

    # Campaigns
    url(
        r'^campaigns/(?P<pk>\d+)/$',
        CampaignIndex.as_view(),
        name='campaign'
    ),
    url(
        r'^campaigns/create/experience/(?P<experience_pk>\d+)/$',
        login_required(CampaignCreate.as_view()),
        name='campaign.create'
    ),
    url(
        r'^campaigns/(?P<pk>\d+)/edit/$',
        login_required(CampaignEdit.as_view()),
        name='campaign.edit'
    ),
    url(
        r'^campaigns/(?P<pk>\d+)/delete/$',
        login_required(CampaignDelete.as_view()),
        name='campaign.delete'
    ),
    url(
        r'^campaigns/(?P<pk>\d+)/paid_bounties/$',
        CampaignPaidBountiesListView.as_view(),
        name='campaign.paid_bounties'
    ),
    url(
        r'^campaigns/(?P<pk>\d+)/fulfilled_bounties/$',
        CampaignFulfilledBountiesListView.as_view(),
        name='campaign.fulfilled_bounties'
    ),

    # Bounties
    url(
        r'^bounties/(?P<pk>\d+)/$',
        BountyIndex.as_view(),
        name='bounty'
    ),
    url(
        r'^campaign/(?P<campaign_pk>\d+)/bounties/', include([
            url(r'^create/$', login_required(BountyCreate.as_view()), name='bounty.create'),
            url(r'^counter/(?P<bounty_pk>\d+)/$', login_required(BountyCreate.as_view()), name='bounty.counter'),
        ]),
    ),
    url(
        r'^bounties/(?P<pk>\d+)/edit/$',
        login_required(BountyEdit.as_view()),
        name='bounty.edit'
    ),
    url(
        r'^bounties/(?P<pk>\d+)/delete/$',
        login_required(BountyDelete.as_view()),
        name='bounty.delete'
    ),
    url(
        r'^bounties/(?P<pk>\d+)/accept/$',
        login_required(BountyAccept.as_view()),
        name='bounty.accept'
    ),
    url(
        r'^bounties/(?P<pk>\d+)/cancel_accept/$',
        login_required(BountyCancelAccept.as_view()),
        name='bounty.cancel_accept'
    ),
)
