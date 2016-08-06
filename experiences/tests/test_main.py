from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.forms.models import model_to_dict

from experiences.models import Experience
from narratives.models import Narrative
from experiences.forms import ExperienceForm
from explorers.tests import helpers as explorer_helpers


class ExperienceTestCase(TestCase):
    experience_title = 'Walk on the Moon'

    def setUp(self):
        self.explorer = explorer_helpers.create_test_explorer_superuser()
        self.explorer_other = explorer_helpers.create_test_explorer()

        self.experience = Experience.objects.create(
            title=self.experience_title,
            author=self.explorer,
            is_public=True)

        self.narrative_public = Narrative.objects.create(
            title='Beginnings',
            body='''I first wanted to go to the moon when I watched a
                documentary and saw Neil Armstrong take the last step from the
                ladder to the lunar surface.''',
            experience = self.experience,
            author=self.explorer,
            is_public=True)
        self.narrative_private = Narrative.objects.create(
            title='Fear',
            body='''Truth be told, I'm afraid of even wanting to tell others I
                want to do this. It becomes eerily real when I do so and I worry
                that if I don't follow through that I will be cast as a
                failure.''',
            experience = self.experience,
            author=self.explorer,
            is_public=False)
