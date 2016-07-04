from django.test import TestCase
from django.db import IntegrityError

from explorers.models import Explorer
from photologue.models import Gallery
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password
from explorers.tests import helpers


class ExplorerTest(TestCase):
    explorer = None
    gallery = None

    def setUp(self):
        self.explorer = helpers.new_explorer()
        self.gallery = Gallery.objects.create(object_pk=self.explorer.id, title="My First Gallery", content_type=ContentType.objects.get_for_model(Explorer))

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
