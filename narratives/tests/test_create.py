from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from narratives.models import Narrative
from narratives.forms import NarrativeForm
from narratives.tests.test_main import NarrativeTestCase
from experiences.forms import ExperienceForm
from experiences.models import Experience


class NarrativeCreateTest(NarrativeTestCase):
    def test_experience_has_narrative(self):
        self.assertIn(self.narrative_public, self.experience.narratives.all())

    def test_narrative_form_submit(self):
        narr_form_context = {
            'experience': self.experience.pk,
            'title': 'Full Moon Tonight!',
            'body': '''I'll be checking it out from my porch with a martini tonight''',
        }
        narr_form = NarrativeForm(narr_form_context, author=self.explorer)
        self.assertTrue(narr_form.is_valid())
        narrative = narr_form.save()
        self.assertIn(narrative, self.experience.narratives.all())
        self.assertTrue(narrative.author == self.explorer)

    def test_author_view_create_new_narrative_page(self):
        self.client.login(username=self.explorer.email,
                password=self.explorer.password_unhashed)
        response = self.client.get(reverse('create_narrative',
            args=(self.experience.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_author_can_create_new_narrative(self):
        narr_title = 'The Martian'
        narr_body = '''I watched the movie today. It was spectacular seeing
            how Matt Damon's character created solutions to the problems.
            Astronauts sure need smarts.'''

        narr_data = {
            'experience': self.experience.pk,
            'title': narr_title,
            'body': narr_body,
            'author': self.explorer.pk
        }
        
        self.client.login(
            username=self.explorer.email,
            password=self.explorer.password_unhashed
        )
        response = self.client.post(
            reverse(
                'create_narrative',
                args=(self.experience.pk,)
            ),
            narr_data
        )
        self.assertTrue(self.experience.narratives.filter(title=narr_title).exists())
        new_narrative = self.experience.narratives.get(title=narr_title)
        self.assertEqual(new_narrative.body, narr_body)

    def test_comrade_can_view_create_new_narrative_page(self):
        self.experience.explorers.add(self.other_explorer)

        self.client.login(
            username=self.other_explorer.email,
            password=self.other_explorer.password_unhashed
        )
        response = self.client.get(reverse('create_narrative',
            args=(self.experience.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_comrade_can_create_new_narrative(self):
        self.experience.explorers.add(self.other_explorer)

        narr_title = 'Ticket Price into Space'
        narr_body = '''As of today, the price of a ticket into space is
            $250,000. Offered by Virgin Galactic'''

        narr_data = {
            'experience': self.experience.pk,
            'title': narr_title,
            'body': narr_body,
            'author': self.other_explorer.pk
        }
        
        self.client.login(
            username=self.other_explorer.email,
            password=self.other_explorer.password_unhashed
        )
        response = self.client.post(
            reverse(
                'create_narrative',
                args=(self.experience.pk,)
            ),
            narr_data
        )
        self.assertTrue(self.experience.narratives.filter(title=narr_title).exists())
        new_narrative = self.experience.narratives.get(title=narr_title)
        self.assertEqual(new_narrative.body, narr_body)

    def test_non_comrade_cant_view_create_new_narrative_page(self):
        self.client.login(
            username=self.other_explorer.email,
            password=self.other_explorer.password_unhashed
        )
        response = self.client.get(reverse('create_narrative',
            args=(self.experience.pk,)))
        self.assertEqual(response.status_code, 403)

    def test_non_comrade_cant_create_new_narrative(self):
        narr_title = 'Buy Louis Vuitton'
        narr_body = '''Act now and get a free purse.
            http://punkd.com/steal-your-info'''

        narr_data = {
            'experience': self.experience.pk,
            'title': narr_title,
            'body': narr_body,
            'author': self.other_explorer.pk
        }
        
        self.client.login(
            username=self.other_explorer.email,
            password=self.other_explorer.password_unhashed
        )
        response = self.client.post(
            reverse(
                'create_narrative',
                args=(self.experience.pk,)
            ),
            narr_data
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.experience.narratives.filter(title=narr_title).exists())

    def test_unauthorized_user_directed_login_to_create_narrative(self):
        response = self.client.get(reverse('create_narrative',
            args=(self.experience.pk,)))
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' +
                reverse('create_narrative', args=(self.experience.pk,)))
