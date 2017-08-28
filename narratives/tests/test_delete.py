from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from narratives.models import Narrative
from narratives.forms import NarrativeForm
from narratives.tests.test_main import NarrativeTestCase
from experiences.forms import ExperienceForm
from experiences.models import Experience


class NarrativeDeleteTest(NarrativeTestCase):
    def test_author_can_view_delete_narrative_page(self):
        self.client.login(
            username=self.explorer.email,
            password=self.explorer.password_unhashed
        )
        response = self.client.get(reverse('delete_narrative',
                args=(self.narrative_public.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_author_can_delete_narrative(self):
        num_narratives_start = self.experience.narratives.count()

        self.client.login(
            username=self.explorer.email,
            password=self.explorer.password_unhashed
        )
        response = self.client.post(
            reverse(
                'delete_narrative',
                args=(self.narrative_public.pk,)
            ),
            {'confirm': True}
        )
        with self.assertRaises(self.narrative_public.DoesNotExist):
            n = Narrative.objects.get(pk=self.narrative_public.pk)

        self.assertNotIn(self.narrative_public, self.experience.narratives.all())

        self.assertRedirects(
            response,
            reverse(
                'experience',
                args=(self.narrative_public.experience.pk,)
            )
        )
        self.assertEqual(
            self.experience.narratives.count(),
            num_narratives_start - 1
        )

    def test_non_author_cannot_delete_narrative(self):
        num_narratives_start = self.experience.narratives.count()

        self.client.login(
            username=self.other_explorer.email,
            password=self.other_explorer.password_unhashed
        )

        response = self.client.post(
            reverse(
                'delete_narrative',
                args=(self.narrative_public.pk,)
            ),
            {'confirm': True}
        )

        self.assertEqual(response.status_code, 403)

        self.assertEqual(
            self.experience.narratives.count(),
            num_narratives_start
        )

    def test_comrade_cannot_view_delete_page(self):
        # Even if they are the author of the experience
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
        response = self.client.get(
            reverse(
                'delete_narrative',
                args=(narrative.pk,)
            )
        )
        self.assertEqual(response.status_code, 403)

    def test_non_logged_in_users_redirect_login_to_view_private_narrative(self):
        response = self.client.get(
            reverse(
                'delete_narrative',
                args=(self.narrative_private.pk,)
            )
        )
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' +
            reverse('delete_narrative', args=(self.narrative_private.pk,)))
