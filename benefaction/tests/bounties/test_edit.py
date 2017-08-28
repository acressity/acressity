from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from benefaction.models import Campaign, Bounty
from benefaction.tests.bounties.test_main import BountyTestCase
from experiences.models import Experience


class BountyEditTest(BountyTestCase):
    def test_author_can_view_edit_own_bounty_page(self):
        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )
        response = self.client.get(reverse('bounty.edit',
                args=(self.bounty_by_author.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_comrade_cannot_view_edit_bounty_page(self):
        self.bounty_by_author.campaign.experience.explorers.add(self.explorer_other)

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.get(reverse('bounty.edit',
                args=(self.bounty_by_author.pk,)))
        self.assertEqual(response.status_code, 403)

    def test_non_comrade_cannot_view_edit_campaign_page(self):
        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.get(reverse('bounty.edit',
                args=(self.bounty_by_author.pk,)))
        self.assertEqual(response.status_code, 403)

    def test_author_cannot_view_edit_bounty_created_by_other_page(self):
        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )
        response = self.client.get(reverse('bounty.edit',
                args=(self.bounty_by_benefactor.pk,)))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_directed_login_to_view_edit_campaign(self):
        response = self.client.post(
            reverse('bounty.edit',
                args=(self.bounty_by_author.pk,))
        )
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' +
                reverse('bounty.edit', args=(self.bounty_by_author.pk,)))

    def test_author_can_edit_own_bounty(self):
        boun_data_edited = {
            'amount': self.bounty_by_author.amount + 100,
            'proposition': self.bounty_by_author.proposition + ' and do a backflip',
        }

        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )
        response = self.client.post(reverse('bounty.edit',
            args=(self.bounty_by_author.pk,)),
            boun_data_edited
        )

        b = Bounty.objects.get(pk=self.bounty_by_author.pk)
        self.assertEqual(b.amount, boun_data_edited['amount'])
        self.assertEqual(b.proposition, boun_data_edited['proposition'])

    def test_author_cannot_edit_bounty_created_by_benefactor(self):
        boun_data_edited = {
            'amount': self.bounty_by_benefactor.amount + 200,
        }

        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )
        response = self.client.post(reverse('bounty.edit',
            args=(self.bounty_by_benefactor.pk,)),
            boun_data_edited
        )

        b = Bounty.objects.get(pk=self.bounty_by_benefactor.pk)
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(b.amount, boun_data_edited['amount'])

    def test_benefactor_can_edit_own_bounty(self):
        boun_data_edited = {
            'amount': self.bounty_by_benefactor.amount - 100,
            'proposition': self.bounty_by_author.proposition,
        }

        self.client.login(
            username=self.explorer_benefactor.email,
            password=self.explorer_benefactor.password_unhashed
        )
        response = self.client.post(reverse('bounty.edit',
            args=(self.bounty_by_benefactor.pk,)),
            boun_data_edited
        )

        b = Bounty.objects.get(pk=self.bounty_by_benefactor.pk)
        self.assertEqual(b.amount, boun_data_edited['amount'])
        self.assertEqual(b.proposition, boun_data_edited['proposition'])

    def test_comrade_cannot_edit_bounty_created_by_author(self):
        self.bounty_by_author.campaign.experience.explorers.add(self.explorer_other)

        boun_data_edited = {
            'amount': self.bounty_by_author.amount + 200,
        }

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.post(reverse('bounty.edit',
            args=(self.bounty_by_author.pk,)),
            boun_data_edited
        )

        b = Bounty.objects.get(pk=self.bounty_by_author.pk)
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(b.amount, boun_data_edited['amount'])

    def test_non_comrade_cannot_edit_bounty(self):
        boun_data_edited = {
            'amount': self.bounty_by_author.amount + 10000,
        }

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.post(reverse('bounty.edit',
            args=(self.bounty_by_author.pk,)),
            boun_data_edited
        )

        b = Bounty.objects.get(pk=self.bounty_by_author.pk)
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(b.amount, boun_data_edited['amount'])

    def test_anonymous_user_directed_login_to_edit_bounty(self):
        boun_data_edited = {
            'amount': self.bounty_by_author.amount + 1000,
        }

        response = self.client.post(
            reverse('bounty.edit',
                args=(self.bounty_by_author.pk,)),
            boun_data_edited
        )
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' +
                reverse('bounty.edit', args=(self.bounty_by_author.pk,)))
