from django.db import IntegrityError
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password

from explorers.models import Explorer
from explorers.tests import helpers
from explorers.tests.test_main import ExplorerTestCase
from experiences.models import Experience
from photologue.models import Gallery


class ExplorerTestEdit(ExplorerTestCase):
    def test_explorer_can_edit_own_profile(self):
        trailname_edited = 'ANeedAnswered'

        expl_data_edited = {
            'trailname': trailname_edited,
            'email': self.explorer.email,
            'first_name': self.explorer.first_name,
            'last_name': self.explorer.last_name,
        }

        self.client.login(
            username=self.explorer.email,
            password=self.explorer.password_unhashed
        )

        response = self.client.post(
            reverse(
                'profile',
                args=(self.explorer.pk,)
            ),
            expl_data_edited
        )

        explorer_edited = Explorer.objects.get(pk=self.explorer.pk)
        self.assertEqual(explorer_edited.trailname, trailname_edited)

    def test_explorer_cannot_edit_other_profile(self):
        expl_data_edited = {
            'trailname': 'Polo',
            'email': 'free_polo@scam.com',
            'first_name': 'Ralph',
            'last_name': 'Lauren',
        }

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )

        response = self.client.post(
            reverse(
                'profile',
                args=(self.explorer.pk,)
            ),
            expl_data_edited
        )

        self.assertEqual(response.status_code, 403)

    def test_non_logged_cannot_edit_other_profile(self):
        expl_data_edited = {
            'trailname': 'Handbags!',
            'email': 'free_handbags@scam.com',
            'first_name': 'Louis',
            'last_name': 'Vuitton',
        }

        response = self.client.post(
            reverse(
                'profile',
                args=(self.explorer.pk,)
            ),
            expl_data_edited
        )

        self.assertEqual(response.status_code, 403)
