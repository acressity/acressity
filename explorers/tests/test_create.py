from django.db import IntegrityError
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password

from explorers.models import Explorer
from explorers.tests import helpers
from explorers.tests.test_main import ExplorerTestCase
from experiences.models import Experience
from photologue.models import Gallery


class ExplorerTestCreate(ExplorerTestCase):
    def test_verify_explorer_created(self):
        try:
            explorer = Explorer.objects.get(trailname=helpers.TEST_TRAILNAME)
        except Explorer.DoesNotExist:
            self.fail('The explorer was not properly created')
        self.assertEqual(explorer, self.explorer)

    def test_create_explorer_with_experience(self):
        explorer_email = 'alexander@emory.edu'
        experience_title = 'Kayak down the Colorado River'
        explorer_password = 'WalkTheW!ldz142'

        explorer_data = {
            'first_name': 'Chris',
            'last_name': 'McCandless',
            'email': explorer_email,
            'trailname': 'Supertramp',
            'password1': explorer_password,
            'password2': explorer_password,
            'title': experience_title,
        }
        response = self.client.post(
            reverse('register'),
            explorer_data
        )

        try:
            explorer = Explorer.objects.get(email=explorer_email)
        except Explorer.DoesNotExist:
            self.fail('The explorer was not properly created')

        try:
            experience = Experience.objects.get(title=experience_title)
        except Experience.DoesNotExist:
            self.fail('The experience was not properly created')

        self.assertIn(experience, explorer.experiences.all())

    def test_create_explorer_without_experience(self):
        explorer_email = 'norgay@hmi-darjeeling.com'
        explorer_password = 'HimilayasHaunt49'

        explorer_data = {
            'first_name': 'Tenzing',
            'last_name': 'Norgay',
            'email': explorer_email,
            'trailname': 'Sherpa',
            'password1': explorer_password,
            'password2': explorer_password,
        }
        response = self.client.post(
            reverse('register'),
            explorer_data
        )

        try:
            explorer = Explorer.objects.get(email=explorer_email)
        except Explorer.DoesNotExist:
            self.fail('The explorer was not properly created')

    def test_create_explorer_without_trailname(self):
        explorer_email = 'hillary@himalayantrust.org'
        explorer_password = 'ItWa$There8123'

        explorer_data = {
            'first_name': 'Edmund',
            'last_name': 'Hillary',
            'email': explorer_email,
            'password1': explorer_password,
            'password2': explorer_password,
        }
        response = self.client.post(
            reverse('register'),
            explorer_data
        )

        try:
            explorer = Explorer.objects.get(email=explorer_email)
        except Explorer.DoesNotExist:
            self.fail('The explorer was not properly created')

    def test_duplicate_trailname_fails(self):
        with self.assertRaises(IntegrityError):
            new_explorer = Explorer.objects.create(first_name='Lorraine',
                last_name='Tristane', trailname='MachuPikchu')
            new_explorer.save()

    def test_ordered_experiences(self):
        exp1 = Experience.objects.create(title='Climb Mount Everest',
                author=self.explorer)
        exp2 = Experience.objects.create(title='Swim Across English Channel',
                author=self.explorer)

        # Experience with most recent timestamp returned first
        self.assertEquals(list(self.explorer.ordered_experiences()), [exp2, exp1])

        # Featuring an experience brings it to front
        self.explorer.featured_experience = exp1
        self.assertEquals(list(self.explorer.ordered_experiences()), [exp1, exp2])
