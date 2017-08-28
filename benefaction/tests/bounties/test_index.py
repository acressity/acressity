from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from benefaction.models import Campaign, Bounty
from benefaction.tests.bounties.test_main import BountyTestCase
from experiences.models import Experience


class BountyIndexTest(BountyTestCase):
    def test_author_can_view_bounty(self):
        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )
        response = self.client.get(self.bounty_by_author.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_comrade_can_view_bounty(self):
        self.bounty_by_author.campaign.experience.explorers.add(self.explorer_other)

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.get(self.bounty_by_author.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_non_comrade_can_view_bounty(self):
        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.get(self.bounty_by_author.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_anonymous_users_can_view_bounty(self):
        response = self.client.get(self.bounty_by_author.get_absolute_url())
        self.assertEqual(response.status_code, 200)
