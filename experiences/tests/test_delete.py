from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from experiences.models import Experience
from experiences.tests.test_main import ExperienceTestCase
from narratives.models import Narrative
from experiences.forms import ExperienceForm
from explorers.tests import helpers as explorer_helpers


class ExperienceDeleteTest(ExperienceTestCase):
    def test_author_can_delete_experience(self):
        self.client.login(
            username=self.explorer.email,
            password=self.explorer.password_unhashed
        )
        response = self.client.post(
            reverse(
                'delete_experience',
                args=(self.experience.pk,)
            ),
            {'confirm': True}
        )

        with self.assertRaises(Experience.DoesNotExist):
            e = Experience.objects.get(pk=self.experience.pk)

    def test_comrade_cannot_delete_experience(self):
        self.experience.explorers.add(self.explorer_other)

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.post(
            reverse(
                'delete_experience',
                args=(self.experience.pk,)
            ),
            {'confirm': True}
        )

        self.assertEqual(response.status_code, 403)

    def test_non_logged_user_directed_login(self):
        response = self.client.post(
            reverse(
                'delete_experience',
                args=(self.experience.pk,)
            ),
            {'confirm': True}
        )
        
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + 
            reverse('delete_experience', args=(self.experience.pk,)))
        self.assertTrue(Experience.objects.get(pk=self.experience.pk))

    def test_author_can_nominate_comrade_as_new_experience_author(self):
        self.experience.explorers.add(self.explorer_other)

        self.client.login(
            username=self.explorer.email,
            password=self.explorer.password_unhashed
        )
        response = self.client.post(
            reverse(
                'delete_experience',
                args=(self.experience.pk,)
            ),
            {
                'nominate': True,
                'explorer_id': self.explorer_other.pk,
            }
        )

        experience = Experience.objects.get(pk=self.experience.pk)
        self.assertEqual(experience.author, self.explorer_other)
        self.assertNotIn(self.explorer, self.experience.explorers.all())

    def test_author_cannot_nominate_non_comrade_as_new_experience_author(self):
        self.client.login(
            username=self.explorer.email,
            password=self.explorer.password_unhashed
        )
        response = self.client.post(
            reverse(
                'delete_experience',
                args=(self.experience.pk,)
            ),
            {
                'nominate': True,
                'explorer_id': self.explorer_other.pk,
            }
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.explorer, self.experience.author)
