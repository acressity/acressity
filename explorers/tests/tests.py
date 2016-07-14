from django.test import TestCase
from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password

from explorers.models import Explorer
from explorers.tests import helpers
from experiences.models import Experience
from photologue.models import Gallery


class ExplorerTest(TestCase):
    explorer = None
    gallery = None

    def setUp(self):
        self.explorer = helpers.new_explorer()
        self.gallery = Gallery.objects.create(object_pk=self.explorer.id, title='My First Gallery', content_type=ContentType.objects.get_for_model(Explorer))

    def test_verify_explorer_created(self):
        explorer = Explorer.objects.get(trailname='MachuPikchu')
        self.assertIsNotNone(explorer)
        self.assertEqual(explorer, self.explorer)

    def test_assign_gallery(self):
        self.assertIsNotNone(self.gallery)
        self.assertEqual(self.gallery.object(), self.explorer)

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

        self.explorer.experiences.add(exp1)
        self.explorer.experiences.add(exp2)
        
        # Experience with most recent timestamp returned first
        self.assertEquals(list(self.explorer.ordered_experiences()), [exp2, exp1])

        # Featuring experience brings it to front
        self.explorer.featured_experience = exp1
        self.assertEquals(list(self.explorer.ordered_experiences()), [exp1, exp2])
