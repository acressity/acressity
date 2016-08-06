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


class ExperienceCreateTest(ExperienceTestCase):
    def test_experience_created(self):
        self.assertEqual(self.experience_title, str(self.experience))

    def test_explorer_has_experience(self):
        self.assertIn(self.experience, self.explorer.experiences.all())

    def test_experience_form_submit(self):
        exp_form_context = {'title': self.experience_title}
        exp_form = ExperienceForm(exp_form_context, author=self.explorer)
        self.assertTrue(exp_form.is_valid())
        experience = exp_form.save()
        self.assertTrue(experience in self.explorer.experiences.all())
        self.assertTrue(experience.author == self.explorer)

    def test_latest_narratives(self):
        narr1 = Narrative.objects.create(
            experience=self.experience,
            author=self.explorer,
            title='To be an astronaut...',
            body='''There were two astronauts lucky enough to make it into
            space today!''',
            is_public=True)
        self.assertEqual(self.experience.public_narratives().count(), 2)
        self.assertEqual(self.experience.narratives.count(), 3)
        self.assertEqual(self.experience.latest_narrative(), narr1)
        self.assertEqual(self.experience.latest_public_narrative(), narr1)

        narr2 = Narrative.objects.create(
            experience=self.experience,
            author=self.explorer,
            title='Celestial Beauty',
            body='''There was a full moon tonight''',
            is_public=False)
        self.assertEqual(self.experience.public_narratives().count(), 2)
        self.assertEqual(self.experience.narratives.count(), 4)
        self.assertEqual(self.experience.latest_narrative(), narr2)
        self.assertEqual(self.experience.latest_public_narrative(), narr1)

    def test_default_privacy(self):
        experience = Experience.objects.create(author=self.explorer,
                title='Swim beside a dolphin')
        self.assertFalse(experience.is_public)

        public_experience = Experience.objects.create(author=self.explorer,
                title='Have a pet dog', is_public=True)
        self.assertTrue(public_experience.is_public)

    def test_explorer_can_create_experience(self):
        experience_title = 'Learn to Fly'
        exp_data = {
            'title': experience_title,
            'author': self.explorer.pk,
        }

        self.client.login(username=self.explorer.email,
                password=self.explorer.password_unhashed)
        response = self.client.post(
            reverse('create_experience'),
            exp_data
        )

        experience = Experience.objects.get(title=experience_title)
        self.assertRedirects(
            response,
            reverse(
                'experience',
                args=(experience.pk,)
            )
        )
        self.assertEqual(experience.title, experience_title)
        self.assertIn(experience, self.explorer.experiences.all())
        
    def test_non_logged_user_directed_login(self):
        experience_title = 'Rolex Watche$: Impre$$ Her the Right Way!!!'
        exp_data = {
            'title': experience_title,
            'author': self.explorer.pk, # They got an existant explorer's ID
        }

        response = self.client.post(
            reverse('create_experience'),
            exp_data
        )

        self.assertRedirects(
            response,
            settings.LOGIN_URL + '?next=' + reverse('create_experience')
        )
            
        with self.assertRaises(Experience.DoesNotExist):
            experience = Experience.objects.get(title=experience_title)
