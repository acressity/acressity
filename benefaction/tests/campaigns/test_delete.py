from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from benefaction.models import Campaign, Bounty
from benefaction.tests.campaigns.test_main import CampaignTestCase
from experiences.models import Experience


class CampaignDeleteTest(CampaignTestCase):
    def test_author_can_view_delete_campaign_page(self):
        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )
        response = self.client.get(reverse('campaign.delete',
                args=(self.campaign.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_comrade_cannot_view_delete_campaign_page(self):
        self.campaign.experience.explorers.add(self.explorer_other)

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.get(reverse('campaign.delete',
                args=(self.campaign.pk,)))
        self.assertEqual(response.status_code, 403)

    def test_non_comrade_cannot_view_delete_campaign_page(self):
        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.get(reverse('campaign.delete',
                args=(self.campaign.pk,)))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_directed_login_to_view_delete_campaign(self):
        response = self.client.get(
            reverse('campaign.delete',
                args=(self.campaign.pk,))
        )
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' +
                reverse('campaign.delete', args=(self.campaign.pk,)))

    def test_author_can_delete_campaign(self):
        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )
        response = self.client.post(reverse('campaign.delete',
                args=(self.campaign.pk,)))

        with self.assertRaises(Campaign.DoesNotExist):
            c = Campaign.objects.get(pk=self.campaign.pk)

    def test_comrade_cannot_delete_campaign(self):
        self.campaign.experience.explorers.add(self.explorer_other)

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.post(reverse('campaign.delete',
                args=(self.campaign.pk,)))

        self.assertEqual(response.status_code, 403)
        c = Campaign.objects.get(pk=self.campaign.pk)
        self.assertEqual(c.experience, self.campaign_experience)

    def test_non_comrade_cannot_delete_campaign(self):
        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.post(reverse('campaign.delete',
                args=(self.campaign.pk,)))

        self.assertEqual(response.status_code, 403)
        c = Campaign.objects.get(pk=self.campaign.pk)
        self.assertEqual(c.experience, self.campaign_experience)

    def test_anonymous_user_directed_login_to_delete_campaign(self):
        response = self.client.post(
            reverse('campaign.delete',
                args=(self.campaign.pk,))
        )
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' +
                reverse('campaign.delete', args=(self.campaign.pk,)))
