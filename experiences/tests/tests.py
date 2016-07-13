from django.test import TestCase

from experiences.models import Experience
from narratives.models import Narrative
from experiences.forms import ExperienceForm
from explorers.tests import helpers


class ExperienceTest(TestCase):
    experience_title = 'Walk on the Moon'

    def setUp(self):
        self.explorer = helpers.new_explorer()
        self.experience = Experience.objects.create(title=self.experience_title,
                author=self.explorer, is_public=True)
        self.explorer.experiences.add(self.experience)

    def test_experience_created(self):
        self.assertEqual(self.experience_title, str(self.experience))

    def test_explorer_has_experience(self):
        self.assertTrue(self.experience in self.explorer.experiences.all())

    def test_experience_form_submit(self):
        exp_form_context = {'title': self.experience_title}
        exp_form = ExperienceForm(exp_form_context, author=self.explorer)
        self.assertTrue(exp_form.is_valid())
        experience = exp_form.save()
        self.assertTrue(experience in self.explorer.experiences.all())
        self.assertTrue(experience.author == self.explorer)


    def test_latest_narratives(self):
        narr1 = Narrative.objects.create(experience=self.experience,
                author=self.explorer, narrative='''There were two astronauts
                lucky enough to make it into space today!''')
        self.assertTrue(self.experience.public_narratives().count() == 1)
        self.assertTrue(self.experience.narratives.count() == 1)
        self.assertEqual(self.experience.latest_narrative(), narr1)
        self.assertEqual(self.experience.latest_public_narrative(), narr1)

        narr2 = Narrative.objects.create(experience=self.experience,
                author=self.explorer, narrative='''There was a full moon
                tonight''', is_public=False)
        self.assertTrue(self.experience.public_narratives().count() == 1)
        self.assertTrue(self.experience.narratives.count() == 2)
        self.assertEqual(self.experience.latest_narrative(), narr2)
        self.assertEqual(self.experience.latest_public_narrative(), narr1)

