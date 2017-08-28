from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.db import transaction, IntegrityError
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from benefaction.models import Campaign, Bounty
from benefaction.tests.bounties.test_main import BountyTestCase
from experiences.models import Experience
from notifications.models import Notification


class BountyAcceptTest(BountyTestCase):
    def test_author_can_accept_bounty_from_benefactor(self):
        self.assertFalse(self.bounty_by_benefactor.is_accepted)

        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.accept', args=(self.bounty_by_benefactor.pk,))
        )
        bounty_by_benefactor_updated = Bounty.objects.get(pk=self.bounty_by_benefactor.pk)

        self.assertTrue(bounty_by_benefactor_updated.is_accepted)

    def test_author_redirected_when_accept_accepted_bounty(self):
        self.bounty_by_benefactor.is_accepted = True
        self.bounty_by_benefactor.save()
        self.assertTrue(self.bounty_by_benefactor.is_accepted)

        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.accept', args=(self.bounty_by_benefactor.pk,))
        )

        self.assertEqual(response.status_code, 302)

    def test_author_cannot_accept_own_bounty(self):
        self.assertFalse(self.bounty_by_benefactor.is_accepted)

        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.accept', args=(self.bounty_by_author.pk,))
        )
        bounty_by_benefactor_updated = Bounty.objects.get(pk=self.bounty_by_benefactor.pk)

        self.assertFalse(bounty_by_benefactor_updated.is_accepted)
        self.assertEqual(response.status_code, 403)

    def test_benefactor_cannot_accept_own_bounty(self):
        self.assertFalse(self.bounty_by_benefactor.is_accepted)

        self.client.login(
            username=self.explorer_benefactor.email,
            password=self.explorer_benefactor.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.accept', args=(self.bounty_by_benefactor.pk,))
        )
        bounty_by_benefactor_updated = Bounty.objects.get(pk=self.bounty_by_benefactor.pk)

        self.assertFalse(bounty_by_benefactor_updated.is_accepted)
        self.assertEqual(response.status_code, 403)

    def test_comrade_cannot_accept_bounty_from_benefactor(self):
        self.campaign_experience.explorers.add(self.explorer_other)
        self.assertFalse(self.bounty_by_benefactor.is_accepted)

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.accept', args=(self.bounty_by_benefactor.pk,))
        )
        bounty_by_benefactor_updated = Bounty.objects.get(pk=self.bounty_by_benefactor.pk)

        self.assertFalse(bounty_by_benefactor_updated.is_accepted)
        self.assertEqual(response.status_code, 403)

    def test_non_comrade_cannot_accept_bounty_from_benefactor(self):
        self.assertFalse(self.bounty_by_benefactor.is_accepted)

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.accept', args=(self.bounty_by_benefactor.pk,))
        )
        bounty_by_benefactor_updated = Bounty.objects.get(pk=self.bounty_by_benefactor.pk)

        self.assertFalse(bounty_by_benefactor_updated.is_accepted)
        self.assertEqual(response.status_code, 403)

    def test_author_accept_bounty_notifies_benefactor(self):
        num_benefactor_notifications = Notification.objects.filter(recipient=self.explorer_benefactor).count()

        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.accept', args=(self.bounty_by_benefactor.pk,))
        )

        self.assertEqual(
            Notification.objects.filter(recipient=self.explorer_benefactor).count(),
            num_benefactor_notifications + 1
        )

    def test_anonymous_user_directed_login_to_accept_bounty(self):
        response = self.client.post(
            reverse('bounty.accept', args=(self.bounty_by_benefactor.pk,))
        )

        self.assertRedirects(
            response,
            settings.LOGIN_URL + '?next=' + reverse('bounty.accept', args=(self.bounty_by_benefactor.pk,))
        )
