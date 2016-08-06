from django.db import IntegrityError
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password

from explorers.models import Explorer
from explorers.tests import helpers
from explorers.tests.test_main import ExplorerTestCase
from experiences.models import Experience
from photologue.models import Gallery


class ExplorerTestDelete(ExplorerTestCase):
    def test_explorer_can_delete_self(self):
        self.client.login(
            username=self.explorer.email,
            password=self.explorer.password_unhashed
        )

        response = self.client.post(
            reverse(
                'explorer.delete',
                args=(self.explorer.pk,)
            ),
            {
                'confirm': True,
            }
        )

        with self.assertRaises(Explorer.DoesNotExist):
            e = Explorer.objects.get(pk=self.explorer.pk)

    def test_explorer_cannot_delete_other(self):
        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )

        response = self.client.post(
            reverse(
                'explorer.delete',
                args=(self.explorer.pk,)
            ),
            {
                'confirm': True,
            }
        )

        try:
            e = Explorer.objects.get(pk=self.explorer.pk)
        except Explorer.DoesNotExist:
            self.fail('Explorer was deleted without authorization')

    def test_non_logged_directed_login(self):
        response = self.client.post(
            reverse(
                'explorer.delete',
                args=(self.explorer.pk,)
            ),
            {
                'confirm': True,
            }
        )

        self.assertRedirects(
            response,
            settings.LOGIN_URL + '?next=' +
                reverse('explorer.delete', args=(self.explorer.pk,))
        )

