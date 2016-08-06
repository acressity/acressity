from django.db import IntegrityError
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password

from explorers.models import Explorer
from explorers.tests import helpers
from explorers.tests.test_main import ExplorerTestCase
from experiences.models import Experience
from photologue.models import Gallery


class ExplorerTestIndex(ExplorerTestCase):
    def test_explorer_can_view_own_profile(self):
        self.client.login(
            username=self.explorer.email,
            password=self.explorer.password_unhashed
        )

        response = self.client.get(
            reverse('profile', args=(self.explorer.pk,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['owner'])

    def test_explorer_can_view_other_profile(self):
        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )

        response = self.client.get(
            reverse('profile', args=(self.explorer.pk,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['owner'])

    def test_non_logged_can_view_profile(self):
        response = self.client.get(
            reverse('profile', args=(self.explorer.pk,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['owner'])
