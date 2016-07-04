from django.test import TestCase

from experiences.models import Experience
from explorers.tests import helpers


class ExperienceTest(TestCase):
    experience = None
    experience_string = 'Walk on the moon'

    def setUp(self):
        self.explorer = helpers.new_explorer()
        self.experience = Experience.objects.create(experience=self.experience_string,
                author=self.explorer, is_public=True)

    def test_experience_created(self):
        self.assertEqual(self.experience_string, str(self.experience))
