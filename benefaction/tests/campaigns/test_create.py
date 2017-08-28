from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.db import transaction, IntegrityError
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from benefaction.models import Campaign, Bounty
from benefaction.tests.campaigns.test_main import CampaignTestCase
from experiences.models import Experience


class CampaignCreateTest(CampaignTestCase):
    def test_author_can_create_new_campaign(self):
        camp_data = {
            'amount_requested': 4000,
            'experience': self.experience_sans_campaign,
        }

        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )
        response = self.client.post(
            reverse('campaign.create', args=(self.experience_sans_campaign.pk,)),
            camp_data
        )
        self.assertTrue(self.experience_sans_campaign.has_campaign)

    def test_author_cannot_create_duplicate_campaign(self):
        original_campaign_amount = self.campaign.amount_requested
        camp_data = {
            'amount_requested': original_campaign_amount + 4000,
            'experience': self.campaign.experience,
        }

        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )

        response = self.client.post(
            reverse('campaign.create', args=(self.campaign.experience.pk,)),
            camp_data
        )
        # Explorer should be routed to a redirect
        self.assertEqual(response.status_code, 302)
        # Amount should still be equal to original

    def test_comrade_cannot_create_new_campaign(self):
        self.experience_sans_campaign.explorers.add(self.explorer_other)

        camp_data = {
            'amount_requested': 5000,
            'experience': self.experience_sans_campaign,
        }

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.post(
            reverse('campaign.create', args=(self.experience_sans_campaign.pk,)),
            camp_data
        )
        self.assertEqual(response.status_code, 403)

    def test_non_comrade_cannot_create_new_campaign(self):
        camp_data = {
            'amount_requested': 9999,
            'experience': self.experience_sans_campaign,
        }

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.post(
            reverse('campaign.create', args=(self.experience_sans_campaign.pk,)),
            camp_data
        )
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_directed_login_to_create_campaign(self):
        camp_data = {
            'amount_requested': 9999,
            'experience': self.experience_sans_campaign,
        }

        response = self.client.post(
            reverse('campaign.create', args=(self.experience_sans_campaign.pk,)),
            camp_data
        )
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' +
                reverse('campaign.create', args=(self.experience_sans_campaign.pk,)))
