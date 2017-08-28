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
    def setUp(self):
        super(BountyAcceptTest, self).setUp()
        self.bounty_by_author.is_accepted = True
        self.bounty_by_benefactor.is_accepted = True

        self.bounty_by_author.save()
        self.bounty_by_benefactor.save()

    def test_author_can_cancel_accept_bounty_from_benefactor(self):
        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.cancel_accept', args=(self.bounty_by_benefactor.pk,))
        )
        bounty_by_benefactor_updated = Bounty.objects.get(pk=self.bounty_by_benefactor.pk)

        self.assertFalse(bounty_by_benefactor_updated.is_accepted)

    def test_author_redirected_when_cancel_accept_unaccepted_bounty(self):
        self.bounty_by_benefactor.is_accepted = False
        self.bounty_by_benefactor.save()

        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.cancel_accept', args=(self.bounty_by_benefactor.pk,))
        )

        self.assertEqual(response.status_code, 302)

    def test_author_cannot_cancel_accept_own_bounty(self):
        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.cancel_accept', args=(self.bounty_by_author.pk,))
        )

        self.assertEqual(response.status_code, 403)

    def test_benefactor_cannot_cancel_accept_author_bounty(self):
        self.client.login(
            username=self.explorer_benefactor.email,
            password=self.explorer_benefactor.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.cancel_accept', args=(self.bounty_by_author.pk,))
        )

        self.assertEqual(response.status_code, 403)

    def test_benefactor_cannot_cancel_accept_own_bounty(self):
        self.client.login(
            username=self.explorer_benefactor.email,
            password=self.explorer_benefactor.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.cancel_accept', args=(self.bounty_by_benefactor.pk,))
        )

        self.assertEqual(response.status_code, 403)

    def test_comrade_cannot_cancel_accept_author_bounty(self):
        self.campaign_experience.explorers.add(self.explorer_other)

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.cancel_accept', args=(self.bounty_by_author.pk,))
        )

        self.assertEqual(response.status_code, 403)

    def test_comrade_cannot_cancel_accept_benefactor_bounty(self):
        self.campaign_experience.explorers.add(self.explorer_other)

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.cancel_accept', args=(self.bounty_by_benefactor.pk,))
        )

        self.assertEqual(response.status_code, 403)

    def test_author_cancel_accept_bounty_notifies_benefactor(self):
        num_benefactor_notifications = Notification.objects.filter(recipient=self.explorer_benefactor).count()

        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )

        response = self.client.post(
            reverse('bounty.cancel_accept', args=(self.bounty_by_benefactor.pk,))
        )

        self.assertEqual(
            Notification.objects.filter(recipient=self.explorer_benefactor).count(),
            num_benefactor_notifications + 1
        )

    def test_anonymous_user_directed_login_to_accept_bounty(self):
        response = self.client.post(
            reverse('bounty.cancel_accept', args=(self.bounty_by_benefactor.pk,))
        )

        self.assertRedirects(
            response,
            settings.LOGIN_URL + '?next=' + reverse('bounty.cancel_accept', args=(self.bounty_by_benefactor.pk,))
        )
