from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from experiences.models import Experience
from experiences.tests.test_main import ExperienceTestCase
from narratives.models import Narrative
from narratives.forms import TRANSFER_ACTION_CHOICES
from experiences.forms import ExperienceForm
from explorers.tests import helpers as explorer_helpers


class ExperienceDeleteTest(ExperienceTestCase):
    def setUp(self):
        super(ExperienceDeleteTest, self).setUp()
        self.experience2 = Experience.objects.create(
            author=self.explorer,
            title='Read Don Quixote in Spanish'
        )

    def test_author_can_copy_narratives(self):
        transfer_data = {
            'to_experience_id': self.experience2.pk,
            'narrative_ids': [
                self.narrative_public.pk,
                self.narrative_private.pk,
            ],
            'potential_actions': [
                TRANSFER_ACTION_CHOICES[2][0], # Copy
                TRANSFER_ACTION_CHOICES[2][0], # Copy
            ],
        }

        self.client.login(
            username=self.explorer.email,
            password=self.explorer.password_unhashed
        )
        self.client.post(
            reverse(
                'transfer_narratives',
                args=(self.experience.pk,)
            ),
            transfer_data
        )

        self.assertIn(self.narrative_public, self.experience.narratives.all())
        self.assertTrue(self.experience2.narratives.filter(title=self.narrative_public.title))

        self.assertIn(self.narrative_private, self.experience.narratives.all())
        self.assertTrue(self.experience2.narratives.filter(title=self.narrative_private.title))

    def test_author_can_transfer_narratives(self):
        transfer_data = {
            'to_experience_id': self.experience2.pk,
            'narrative_ids': [
                self.narrative_public.pk,
                self.narrative_private.pk,
            ],
            'potential_actions': [
                TRANSFER_ACTION_CHOICES[1][0], # Transfer
                TRANSFER_ACTION_CHOICES[1][0], # Transfer
            ]
        }

        self.client.login(
            username=self.explorer.email,
            password=self.explorer.password_unhashed
        )
        self.client.post(
            reverse(
                'transfer_narratives',
                args=(self.experience.pk,)
            ),
            transfer_data
        )

        self.assertNotIn(self.narrative_public, self.experience.narratives.all())
        self.assertTrue(self.experience2.narratives.filter(title=self.narrative_public.title))

        self.assertNotIn(self.narrative_private, self.experience.narratives.all())
        self.assertTrue(self.experience2.narratives.filter(title=self.narrative_private.title))

    def test_comrade_can_copy_narratives(self):
        self.experience.explorers.add(self.explorer_other)
        self.experience2.explorers.add(self.explorer_other)

        transfer_data = {
            'to_experience_id': self.experience2.pk,
            'narrative_ids': [
                self.narrative_public.pk,
                self.narrative_private.pk,
            ],
            'potential_actions': [
                TRANSFER_ACTION_CHOICES[2][0], # Copy
                TRANSFER_ACTION_CHOICES[2][0], # Copy
            ],
        }

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        self.client.post(
            reverse(
                'transfer_narratives',
                args=(self.experience.pk,)
            ),
            transfer_data
        )

        self.assertIn(self.narrative_public, self.experience.narratives.all())
        self.assertTrue(self.experience2.narratives.filter(title=self.narrative_public.title))

        self.assertIn(self.narrative_private, self.experience.narratives.all())
        self.assertTrue(self.experience2.narratives.filter(title=self.narrative_private.title))

    def test_comrade_can_transfer_narratives(self):
        self.experience.explorers.add(self.explorer_other)
        self.experience2.explorers.add(self.explorer_other)

        transfer_data = {
            'to_experience_id': self.experience2.pk,
            'narrative_ids': [
                self.narrative_public.pk,
                self.narrative_private.pk,
            ],
            'potential_actions': [
                TRANSFER_ACTION_CHOICES[1][0], # Transfer
                TRANSFER_ACTION_CHOICES[1][0], # Transfer
            ]
        }

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        self.client.post(
            reverse(
                'transfer_narratives',
                args=(self.experience.pk,)
            ),
            transfer_data
        )

        self.assertNotIn(self.narrative_public, self.experience.narratives.all())
        self.assertTrue(self.experience2.narratives.filter(title=self.narrative_public.title))

        self.assertNotIn(self.narrative_private, self.experience.narratives.all())
        self.assertTrue(self.experience2.narratives.filter(title=self.narrative_private.title))

    def test_non_comrade_cannot_copy_narratives(self):
        transfer_data = {
            'to_experience_id': self.experience2.pk,
            'narrative_ids': [
                self.narrative_public.pk,
                self.narrative_private.pk,
            ],
            'potential_actions': [
                TRANSFER_ACTION_CHOICES[2][0], # Copy
                TRANSFER_ACTION_CHOICES[2][0], # Copy
            ],
        }

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.post(
            reverse(
                'transfer_narratives',
                args=(self.experience.pk,)
            ),
            transfer_data
        )

        self.assertEqual(response.status_code, 403)
        self.assertIn(self.narrative_public, self.experience.narratives.all())
        self.assertFalse(self.experience2.narratives.filter(title=self.narrative_public.title))

        self.assertIn(self.narrative_private, self.experience.narratives.all())
        self.assertFalse(self.experience2.narratives.filter(title=self.narrative_private.title))

    def test_non_comrade_cannot_transfer_narratives(self):
        transfer_data = {
            'to_experience_id': self.experience2.pk,
            'narrative_ids': [
                self.narrative_public.pk,
                self.narrative_private.pk,
            ],
            'potential_actions': [
                TRANSFER_ACTION_CHOICES[1][0], # Transfer
                TRANSFER_ACTION_CHOICES[1][0], # Transfer
            ]
        }

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.post(
            reverse(
                'transfer_narratives',
                args=(self.experience.pk,)
            ),
            transfer_data
        )

        self.assertEqual(response.status_code, 403)
        self.assertIn(self.narrative_public, self.experience.narratives.all())
        self.assertFalse(self.experience2.narratives.filter(title=self.narrative_public.title))

        self.assertIn(self.narrative_private, self.experience.narratives.all())
        self.assertFalse(self.experience2.narratives.filter(title=self.narrative_private.title))

    def test_non_logged_directed_login(self):
        transfer_data = {
            'to_experience_id': self.experience2.pk,
            'narrative_ids': [
                self.narrative_public.pk,
                self.narrative_private.pk,
            ],
            'potential_actions': [
                TRANSFER_ACTION_CHOICES[1][0], # Transfer
                TRANSFER_ACTION_CHOICES[1][0], # Transfer
            ]
        }

        response = self.client.post(
            reverse(
                'transfer_narratives',
                args=(self.experience.pk,)
            ),
            transfer_data
        )

        self.assertRedirects(response, settings.LOGIN_URL + '?next=' +
            reverse('transfer_narratives', args=(self.experience.pk,)))

