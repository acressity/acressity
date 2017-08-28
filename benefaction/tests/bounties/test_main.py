from django.test import TestCase, TransactionTestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from benefaction.models import Campaign, Bounty
from experiences.models import Experience
from explorers.tests import helpers as explorer_helpers


class BountyTestCase(TestCase):
    def setUp(self):
        self.explorer_author = explorer_helpers.create_test_explorer_superuser()
        self.explorer_other = explorer_helpers.create_test_explorer()
        self.explorer_benefactor = explorer_helpers.create_test_explorer()

        self.campaign_experience = Experience.objects.create(
            title='Start Candle-Making Operation',
            author=self.explorer_author,
            is_public=True
        )

        self.campaign = Campaign.objects.create(
            experience=self.campaign_experience,
            amount_requested=40000.00
        )

        self.bounty_by_author = Bounty.objects.create(
            campaign=self.campaign,
            creator=self.explorer_author,
            proposition='Pick the name of the business',
            amount=1000,
            description='I do retain veto power'
        )

        self.bounty_by_benefactor = Bounty.objects.create(
            campaign=self.campaign,
            creator=self.explorer_benefactor,
            proposition='Pick the name of the business',
            amount=900,
            description='You do retain veto power'
        )

