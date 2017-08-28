from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.db import transaction, IntegrityError
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from benefaction.models import Campaign, Bounty
from benefaction.tests.bounties.test_main import BountyTestCase
from experiences.models import Experience


class BountyCreateTest(BountyTestCase):
    def test_author_can_create_bounty(self):
        num_bounties_start = self.campaign.bounties.count()

        first_bounty_data = {
            'amount': 500,
            'proposition': 'Pick a flavor',
        }

        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.create', args=(self.campaign.pk,)),
            first_bounty_data
        )
        self.assertEqual(
            self.campaign.bounties.count(),
            num_bounties_start + 1
        )

    def test_comrade_can_create_bounty(self):
        self.bounty_by_author.campaign.experience.explorers.add(self.explorer_other)
        num_bounties_start = self.campaign.bounties.count()

        first_bounty_data = {
            'amount': 100,
            'proposition': 'Receive first candle',
        }

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.create', args=(self.campaign.pk,)),
            first_bounty_data
        )
        self.assertEqual(
            self.campaign.bounties.count(),
            num_bounties_start + 1
        )

    def test_non_comrade_can_create_bounty(self):
        num_bounties_start = self.campaign.bounties.count()

        first_bounty_data = {
            'amount': 30000,
            'proposition': 'Own 20% of business',
        }

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.create', args=(self.campaign.pk,)),
            first_bounty_data
        )
        self.assertEqual(
            self.campaign.bounties.count(),
            num_bounties_start + 1
        )

    def test_anonymous_user_directed_login_to_create_bid(self):
        response = self.client.get(
            reverse('bounty.create', args=(self.campaign.pk,))
        )
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' +
            reverse('bounty.create', args=(self.campaign.pk,)))
