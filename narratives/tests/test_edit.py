from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from narratives.models import Narrative
from narratives.forms import NarrativeForm
from narratives.tests.test_main import NarrativeTestCase
from experiences.forms import ExperienceForm
from experiences.models import Experience


class NarrativeEditTest(NarrativeTestCase):
    def test_unauthorized_user_directed_login_to_edit_narrative(self):
        response = self.client.get(reverse('edit_narrative',
            args=(self.narrative_public.id,)))
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' +
            reverse('edit_narrative', args=(self.narrative_public.pk,)))

    def test_narrative_author_can_view_edit_page(self):
        self.experience.explorers.add(self.other_explorer)

        narrative = Narrative.objects.create(
            author=self.other_explorer,
            experience=self.experience, # author is self.explorer
            title='Good to be On Board',
            body='''I'm happy to be a part of this experience'''
        )

        self.client.login(
            username=self.other_explorer.email,
            password=self.other_explorer.password_unhashed
        )
        response = self.client.get(reverse('edit_narrative',
            args=(narrative.id,)))
        self.assertEqual(response.status_code, 200)

    def test_narrative_author_can_edit_narrative(self):
        title_original = 'Wallace and Gromit'
        title_edited = 'Wallace and Gromit: A Grand Day Out'

        narrative_original = Narrative.objects.create(
            author=self.explorer,
            experience=self.experience,
            title=title_original,
            body='''I love how the moon is made of cheese. Tension during the
                scene where they forget the crackers.'''
        )

        narr_data_edited = {
            'title': title_edited,
            'body': narrative_original.body,
            'experience': narrative_original.experience.pk,
            'author': self.explorer,
        }

        self.client.login(
            username=self.explorer.email,
            password=self.explorer.password_unhashed
        )
        response = self.client.post(
            reverse(
                'edit_narrative',
                args=(narrative_original.id,)
            ),
            narr_data_edited
        )

        narrative_edited = Narrative.objects.get(pk=narrative_original.pk)
        self.assertEqual(narrative_edited.title, title_edited)

    def test_experience_author_cannot_view_edit_page_when_not_author(self):
        # Not even the author of the experience can edit
        self.experience.explorers.add(self.other_explorer)

        narrative = Narrative.objects.create(
            author=self.other_explorer,
            experience=self.experience, # author is self.explorer
            title='Good to be On Board',
            body='''I'm happy to be a part of this experience'''
        )
        self.client.login(
            username=self.explorer.email,
            password=self.explorer.password_unhashed
        )
        response = self.client.get(reverse('edit_narrative',
            args=(narrative.id,)))
        self.assertEqual(response.status_code, 403)

    def test_experience_author_cannot_edit_narrative_when_not_author(self):
        self.experience.explorers.add(self.other_explorer)

        title_original = 'Curiosity'
        title_edited = 'Curiosity Birthday Song'

        narrative_original = Narrative.objects.create(
            author=self.other_explorer,
            experience=self.experience,
            title=title_original,
            body='''I was simultaneously overjoyed and saddened when I learned
                the rover sings happy birthday to itself, all alone in such a
                remote world. I long to feel the surreal awe which must accompany
                such expeditions'''
        )

        narr_data_edited = {
            'title': title_edited,
            'body': narrative_original.body,
            'experience': narrative_original.experience.pk,
            'author': self.other_explorer,
        }

        self.client.login(
            username=self.explorer.email,
            password=self.explorer.password_unhashed
        )
        response = self.client.post(
            reverse(
                'edit_narrative',
                args=(narrative_original.id,)
            ),
            narr_data_edited
        )

        self.assertEqual(response.status_code, 403)
        narrative_edited = Narrative.objects.get(pk=narrative_original.pk)
        self.assertEqual(narrative_edited.title, title_original)
