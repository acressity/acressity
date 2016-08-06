from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.forms.models import model_to_dict

from experiences.models import Experience
from experiences.forms import ExperienceForm
from experiences.tests.test_main import ExperienceTestCase
from narratives.models import Narrative
from explorers.tests import helpers as explorer_helpers


class ExperienceIndexTest(ExperienceTestCase):
    def test_author_can_view_all_narratives(self):
        self.client.login(username=self.explorer.email,
            password=self.explorer.password_unhashed)
        response = self.client.get(
            reverse(
                'experience',
                args=(self.experience.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.narrative_public, response.context['narratives'])
        self.assertIn(self.narrative_private, response.context['narratives'])

    def test_comrade_can_view_all_narratives(self):
        self.experience.explorers.add(self.explorer_other)

        self.client.login(username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed)
        response = self.client.get(
            reverse(
                'experience',
                args=(self.experience.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.narrative_public, response.context['narratives'])
        self.assertIn(self.narrative_private, response.context['narratives'])
                
    def test_non_comrade_can_view_public_narratives(self):
        self.client.login(username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed)
        response = self.client.get(
            reverse(
                'experience',
                args=(self.experience.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.narrative_public, response.context['narratives'])

    def test_non_comrade_cannot_view_private_narratives(self):
        self.client.login(username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed)
        response = self.client.get(
            reverse(
                'experience',
                args=(self.experience.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.narrative_private, response.context['narratives'])

    def test_non_logged_users_can_view_public_narratives(self):
        response = self.client.get(
            reverse(
                'experience',
                args=(self.experience.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.narrative_public, response.context['narratives'])

    def test_non_logged_users_cannot_view_private_narratives(self):
        response = self.client.get(
            reverse(
                'experience',
                args=(self.experience.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.narrative_private, response.context['narratives'])
