from django.test import TestCase

from experiences.models import Experience
from narratives.models import Narrative
from narratives.forms import NarrativeForm
from experiences.forms import ExperienceForm
from explorers.tests import helpers as explorer_helpers


class NarrativeTest(TestCase):
    experience_title = 'Walk on the Moon'

    def setUp(self):
        self.explorer = explorer_helpers.new_explorer()
        self.experience = Experience.objects.create(title=self.experience_title, author=self.explorer, is_public=True)
        self.narrative = Narrative.objects.create(
            title='I remember when Neil Armstrong landed on the moon',
            body='''It was at that moment I knew I wanted to experience that
            awe he surely did as he gazed back towards our multicolored
            marble. A world away, but feeling more intimate a connection than most
            treading its surface.''',
            author=self.explorer,
            experience=self.experience)

    def test_experience_has_narrative(self):
        self.assertIn(self.narrative, self.experience.narratives.all())

    def test_narrative_form_submit(self):
        narr_form_context = {
            'experience': self.experience.pk,
            'experience_id': self.experience.pk,
            'title': 'Full Moon Tonight!',
            'body': '''I'll be checking it out from my porch with a martini tonight''',
        }
        narr_form = NarrativeForm(narr_form_context, author=self.explorer)
        self.assertTrue(narr_form.is_valid())
        narrative = narr_form.save()
        self.assertIn(narrative, self.experience.narratives.all())
        self.assertTrue(narrative.author == self.explorer)

