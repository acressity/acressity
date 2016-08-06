from django.test import TestCase
from django.db import IntegrityError
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password

from explorers.models import Explorer
from explorers.tests import helpers
from experiences.models import Experience
from photologue.models import Gallery


class ExplorerTestCase(TestCase):
    def setUp(self):
        self.explorer = helpers.create_test_explorer_superuser()
        self.explorer_other = helpers.create_test_explorer()
