from django.test import TestCase

from experiences.models import Experience
from experiences.forms import ExperienceForm
from explorers.tests import helpers


class ExperienceTest(TestCase):
    experience_string = 'Walk on the moon'

    def setUp(self):
        self.explorer = helpers.new_explorer()
        self.experience = Experience.objects.create(experience=self.experience_string,
                author=self.explorer, is_public=True)
        self.explorer.experiences.add(self.experience)

    def test_experience_created(self):
        self.assertEqual(self.experience_string, str(self.experience))

    def test_explorer_has_experience(self):
        self.assertTrue(self.experience in self.explorer.experiences.all())

    def test_experience_form_submit(self):
        exp_form_context = {'experience': self.experience_string}
        exp_form = ExperienceForm(exp_form_context, author=self.explorer)
        self.assertTrue(exp_form.is_valid())
        experience = exp_form.save()
        self.assertTrue(experience in self.explorer.experiences.all())
        self.assertTrue(experience.author == self.explorer)
