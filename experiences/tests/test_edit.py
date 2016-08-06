from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.forms.models import model_to_dict

from experiences.models import Experience
from experiences.tests.test_main import ExperienceTestCase
from narratives.models import Narrative
from experiences.forms import ExperienceForm
from explorers.tests import helpers as explorer_helpers
 

class ExperienceEditTest(ExperienceTestCase):
    def test_non_logged_directed_to_login(self):
        response = self.client.get(
            reverse('edit_experience', args=(self.experience.pk,))
        )
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' +
                reverse('edit_experience', args=(self.experience.pk,)))

    def test_author_can_edit_experience(self):
        title_original = self.experience.title
        title_edited = 'Go to Outer Space'

        exp_data_edited = {
            'title': title_edited,
            'author': self.explorer,
        }
        
        self.client.login(
            username=self.explorer.email,
            password=self.explorer.password_unhashed
        )
        response = self.client.post(
            reverse('edit_experience', args=(self.experience.pk,)),
            exp_data_edited
        )

        experience_edited = Experience.objects.get(pk=self.experience.pk)
        self.assertEqual(experience_edited.title, title_edited)

    def test_comrade_can_edit_experience(self):
        self.experience.explorers.add(self.explorer_other)

        title_original = self.experience.title
        title_edited = 'Play Golf on the Moon'

        exp_data_edited = {
            'title': title_edited,
            'author': self.explorer,
        }
        
        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.post(
            reverse('edit_experience', args=(self.experience.pk,)),
            exp_data_edited
        )

        experience_edited = Experience.objects.get(pk=self.experience.pk)
        self.assertEqual(experience_edited.title, title_edited)

    def test_non_comrade_cannot_edit_experience(self):
        title_original = self.experience.title
        title_edited = 'Do you want to add inches to your flagpole???'

        exp_data_edited = {
            'title': title_edited,
            'author': self.explorer,
        }
        
        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.post(
            reverse('edit_experience', args=(self.experience.pk,)),
            exp_data_edited
        )

        self.assertEqual(response.status_code, 403)
        experience_edited = Experience.objects.get(pk=self.experience.pk)
        self.assertEqual(experience_edited.title, title_original)
