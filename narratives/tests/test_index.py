from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from narratives.models import Narrative
from narratives.forms import NarrativeForm
from narratives.tests.test_main import NarrativeTestCase
from experiences.forms import ExperienceForm
from experiences.models import Experience

class NarrativeIndexTest(NarrativeTestCase):
    def test_author_can_view_private_narrative(self):
        # Creator can access
        self.client.login(username=self.explorer.email, password=self.explorer.password_unhashed)
        response = self.client.get(reverse('narrative',
            args=(self.narrative_private.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_comrade_can_view_private_narrative(self):
        self.experience.explorers.add(self.other_explorer)

        self.client.login(username=self.other_explorer.email, password=self.other_explorer.password_unhashed)
        response = self.client.get(reverse('narrative',
            args=(self.narrative_private.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_non_logged_in_users_redirect_login_to_view_private_narrative(self):
        response = self.client.get(reverse('narrative',
            args=(self.narrative_private.pk,)))
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' +
                reverse('narrative', args=(self.narrative_private.pk,)))

    def test_non_comrade_cant_view_private_narrative(self):
        self.client.login(username=self.other_explorer.email, password=self.other_explorer.password_unhashed)
        response = self.client.get(reverse('narrative',
            args=(self.narrative_private.pk,)))
        self.assertEqual(response.status_code, 403)


