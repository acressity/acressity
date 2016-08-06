from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from experiences.models import Experience
from narratives.models import Narrative
from narratives.forms import NarrativeForm
from experiences.forms import ExperienceForm
from explorers.tests import helpers as explorer_helpers


class NarrativeTestCase(TestCase):
    def setUp(self):
        self.explorer = explorer_helpers.create_test_explorer_superuser()
        self.other_explorer = explorer_helpers.create_test_explorer()

        self.experience = Experience.objects.create(
            title='Walk on the Moon',
            author=self.explorer,
            is_public=True)

        self.narrative_public = Narrative.objects.create(
            title='I remember when Neil Armstrong landed on the moon',
            body='''It was at that moment I knew I wanted to experience that
            awe he surely did as he gazed back towards our multicolored
            marble. A world away, but feeling more intimate a connection than most
            treading its surface.''',
            author=self.explorer,
            experience=self.experience
        )

        self.narrative_private = Narrative.objects.create(title='Private Narrative',
            author=self.explorer,
            experience=self.experience,
            body='Thinking about space scares me more than I care to admit', 
            is_public=False
        )
