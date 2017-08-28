from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from benefaction.models import Campaign, Bounty
from benefaction.tests.campaigns.test_main import CampaignTestCase
from experiences.models import Experience


class CampaignEditTest(CampaignTestCase):
    def test_author_can_view_edit_campaign_page(self):
        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )
        response = self.client.get(reverse('campaign.edit',
                args=(self.campaign.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_comrade_cannot_view_edit_campaign_page(self):
        self.campaign.experience.explorers.add(self.explorer_other)

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.get(reverse('campaign.edit',
                args=(self.campaign.pk,)))
        self.assertEqual(response.status_code, 403)

    def test_non_comrade_cannot_view_edit_campaign_page(self):
        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.get(reverse('campaign.edit',
                args=(self.campaign.pk,)))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_directed_login_to_view_edit_campaign(self):
        response = self.client.post(
            reverse('campaign.edit',
                args=(self.campaign.pk,))
        )
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' +
                reverse('campaign.edit', args=(self.campaign.pk,)))

    def test_author_can_edit_campaign_page(self):
        amount_requested_edited = self.campaign.amount_requested + 1000

        camp_data_edited = {
            'amount_requested': amount_requested_edited,
        }

        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )
        response = self.client.post(reverse('campaign.edit',
            args=(self.campaign.pk,)),
            camp_data_edited
        )

        c = Campaign.objects.get(pk=self.campaign.pk)
        self.assertEqual(c.amount_requested, amount_requested_edited)

    def test_comrade_cannot_edit_campaign_page(self):
        self.campaign.experience.explorers.add(self.explorer_other)

        amount_requested_edited = self.campaign.amount_requested + 2000

        camp_data_edited = {
            'amount_requested': amount_requested_edited,
        }

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.post(reverse('campaign.edit',
            args=(self.campaign.pk,)),
            camp_data_edited
        )

        c = Campaign.objects.get(pk=self.campaign.pk)
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(c.amount_requested, amount_requested_edited)

    def test_non_comrade_cannot_edit_campaign_page(self):
        amount_requested_edited = self.campaign.amount_requested + 10000

        camp_data_edited = {
            'amount_requested': amount_requested_edited,
        }

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.post(reverse('campaign.edit',
            args=(self.campaign.pk,)),
            camp_data_edited
        )

        c = Campaign.objects.get(pk=self.campaign.pk)
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(c.amount_requested, amount_requested_edited)

    def test_anonymous_user_directed_login_to_edit_campaign(self):
        amount_requested_edited = self.campaign.amount_requested + 10000

        camp_data_edited = {
            'amount_requested': amount_requested_edited,
        }

        response = self.client.post(
            reverse('campaign.edit',
                args=(self.campaign.pk,)),
            camp_data_edited
        )
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' +
                reverse('campaign.edit', args=(self.campaign.pk,)))
