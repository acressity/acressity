from django.test import TestCase, RequestFactory, TransactionTestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from benefaction.models import Campaign, Bounty
from experiences.models import Experience
from explorers.tests import helpers as explorer_helpers


class CampaignTestCase(TestCase):
    def setUp(self):
        self.explorer_author = explorer_helpers.create_test_explorer_superuser()
        self.explorer_benefactor = explorer_helpers.create_test_explorer()
        self.explorer_other = explorer_helpers.create_test_explorer()

        self.campaign_experience = Experience.objects.create(
            title='Kayak the Colorado River',
            author=self.explorer_author,
            is_public=True
        )

        self.campaign = Campaign.objects.create(
            experience=self.campaign_experience,
            amount_requested=4000
        )

        self.experience_sans_campaign = Experience.objects.create(
            title='Build a School',
            author=self.explorer_author,
            is_public=True
        )
