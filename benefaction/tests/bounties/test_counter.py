from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.db import transaction, IntegrityError
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from benefaction.models import Campaign, Bounty
from benefaction.tests.bounties.test_main import BountyTestCase
from experiences.models import Experience
from notifications.models import Notification


class BountyCounterTest(BountyTestCase):
    def test_author_can_create_counter_to_benefactor_bounty(self):
        counter_amount = self.bounty_by_benefactor.amount + 113
        num_bounties_start = self.campaign.bounties.count()

        self.assertFalse(self.bounty_by_benefactor.get_children().exists())

        new_counter_data = {
            'parent': self.bounty_by_benefactor.pk,
            'creator': self.explorer_author,
            'amount': counter_amount,
            'proposition': self.bounty_by_benefactor.proposition,
        }

        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.counter', args=(self.campaign.pk, self.bounty_by_benefactor.pk)),
            new_counter_data
        )

        self.assertEqual(
            self.campaign.bounties.count(),
            num_bounties_start + 1
        )
        self.assertTrue(self.bounty_by_benefactor.get_children().exists())

    def test_author_counter_notifies_benefactor(self):
        num_benefactor_notifications = Notification.objects.filter(recipient=self.explorer_benefactor).count()

        new_counter_data = {
            'parent': self.bounty_by_benefactor.pk,
            'amount': self.bounty_by_benefactor.amount + 12,
            'proposition': self.bounty_by_benefactor.proposition,
        }

        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.counter', args=(self.campaign.pk, self.bounty_by_benefactor.pk,)),
            new_counter_data
        )

        self.assertEqual(
            Notification.objects.filter(recipient=self.explorer_benefactor).count(),
            num_benefactor_notifications + 1
        )

    def test_comrade_can_create_counter_to_benefactor_bounty(self):
        self.campaign_experience.explorers.add(self.explorer_other)

        counter_description = self.bounty_by_benefactor.description + ' Must be in USA'
        num_bounties_start = self.campaign.bounties.count()

        self.assertFalse(self.bounty_by_benefactor.get_children().exists())

        new_counter_data = {
            'parent': self.bounty_by_benefactor.pk,
            'amount': self.bounty_by_benefactor.amount,
            'proposition': self.bounty_by_benefactor.proposition,
            'description': counter_description,
        }

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.counter', args=(self.campaign.pk, self.bounty_by_benefactor.pk,)),
            new_counter_data
        )

        self.assertEqual(
            self.campaign.bounties.count(),
            num_bounties_start + 1
        )
        self.assertTrue(self.bounty_by_benefactor.get_children().exists())

    def test_non_comrade_can_create_counterbid_to_benefactor_bid(self):
        counter_amount = self.bounty_by_benefactor.amount - 108
        num_bounties_start = self.campaign.bounties.count()

        self.assertFalse(self.bounty_by_benefactor.get_children().exists())

        new_counter_data = {
            'parent': self.bounty_by_benefactor.pk,
            'amount': counter_amount,
            'proposition': self.bounty_by_benefactor.proposition,
            'description': self.bounty_by_benefactor.description,
        }

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.counter', args=(self.campaign.pk, self.bounty_by_benefactor.pk,)),
            new_counter_data
        )

        self.assertEqual(
            self.campaign.bounties.count(),
            num_bounties_start + 1
        )

        self.assertTrue(self.bounty_by_benefactor.get_children().exists())

    def test_anonymous_user_directed_login_to_create_counterbid_to_benefactor_bid(self):
        response = self.client.post(
            reverse('bounty.counter', args=(self.campaign.pk, self.bounty_by_benefactor.pk,)),
            {
                'parent': self.bounty_by_benefactor.pk,
                'amount': self.bounty_by_benefactor.amount + 99999,
                'proposition': self.bounty_by_benefactor.proposition,
            }
        )
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' +
            reverse('bounty.counter', args=(self.campaign.pk, self.bounty_by_benefactor.pk,)))

    def test_benefactor_can_create_counterbid_to_author_bid(self):
        counter_amount = self.bounty_by_author.amount - 78
        num_bounties_start = self.campaign.bounties.count()

        self.assertFalse(self.bounty_by_author.get_children().exists())

        new_counter_data = {
            'parent': self.bounty_by_author.pk,
            'amount': counter_amount,
            'proposition': self.bounty_by_author.proposition,
            'description': self.bounty_by_author.description,
        }

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.counter', args=(self.campaign.pk, self.bounty_by_author.pk,)),
            new_counter_data
        )

        self.assertEqual(
            self.campaign.bounties.count(),
            num_bounties_start + 1
        )

        self.assertTrue(self.bounty_by_author.get_children().exists())

    def test_benefactor_counterbid_notifies_author(self):
        num_author_notifications = Notification.objects.filter(recipient=self.explorer_author).count()

        new_counter_data = {
            'parent': self.bounty_by_author.pk,
            'amount': self.bounty_by_benefactor.amount - 12,
            'proposition': self.bounty_by_benefactor.proposition,
            'description': self.bounty_by_benefactor.description,
        }

        self.client.login(
            username=self.explorer_benefactor.email,
            password=self.explorer_benefactor.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.counter', args=(self.campaign.pk, self.bounty_by_author.pk)),
            new_counter_data
        )

        self.assertEqual(
            Notification.objects.filter(recipient=self.explorer_author).count(),
            num_author_notifications + 1
        )

    def test_comrade_can_create_counterbid_to_author_bid(self):
        self.campaign_experience.explorers.add(self.explorer_other)

        counter_proposition = self.bounty_by_author.proposition + ' and Do a Backflip'
        num_bounties_start = self.campaign.bounties.count()

        self.assertFalse(self.bounty_by_author.get_children().exists())

        new_counter_data = {
            'parent': self.bounty_by_author.pk,
            'amount': self.bounty_by_author.amount,
            'proposition': counter_proposition,
            'description': self.bounty_by_author.description,
        }

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.counter', args=(self.campaign.pk, self.bounty_by_author.pk,)),
            new_counter_data
        )

        self.assertEqual(
            self.campaign.bounties.count(),
            num_bounties_start + 1
        )

        self.assertTrue(self.bounty_by_author.get_children().exists())

    def test_non_comrade_can_create_counterbid_to_author_bid(self):
        counter_proposition = self.bounty_by_author.proposition + ' while dancing Thriller'
        num_bounties_start = self.campaign.bounties.count()

        self.assertFalse(self.bounty_by_author.get_children().exists())

        new_counter_data = {
            'parent': self.bounty_by_author.pk,
            'amount': self.bounty_by_author.amount,
            'proposition': counter_proposition,
            'description': self.bounty_by_author.description,
        }

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.counter', args=(self.campaign.pk, self.bounty_by_benefactor.pk,)),
            new_counter_data
        )

        self.assertEqual(
            self.campaign.bounties.count(),
            num_bounties_start + 1
        )

        self.assertTrue(self.bounty_by_author.get_children().exists())

    def test_anonymous_user_directed_login_to_create_counterbid_to_author_bid(self):
        response = self.client.post(
            reverse('bounty.counter', args=(self.campaign.pk, self.bounty_by_author.pk)),
            {
                'parent': self.bounty_by_author.pk,
                'amount': self.bounty_by_author.amount + 99999,
                'proposition': self.bounty_by_author.proposition,
                'description': self.bounty_by_author.description,
            }
        )
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' +
            reverse('bounty.counter', args=(self.campaign.pk, self.bounty_by_author.pk)))

