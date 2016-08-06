import random
import string

from django.contrib.auth.hashers import make_password

from explorers.models import Explorer

TEST_TRAILNAME = 'MachuPikchu'

def create_test_explorer_superuser():
    password = 'D0N_QU!XOTE_5'

    explorer = Explorer.objects.create(
        first_name='Dwain',
        last_name='Dedrick',
        trailname=TEST_TRAILNAME,
        password=make_password(password),
        email='dwain@somewhere.edu',
        is_superuser=True
    )
    explorer.password_unhashed = password

    return explorer

def create_test_explorer():
    first_name = _random_name()
    password = _random_name()

    explorer = Explorer.objects.create(
        first_name=first_name,
        last_name=_random_name(),
        trailname=_random_name(),
        password=make_password(password),
        email=_random_email(name=first_name)
    )
    explorer.password_unhashed = password

    return explorer

def _random_name(letters=7):
    name = random.choice(string.ascii_uppercase)
    return name + ''.join([random.choice(string.ascii_lowercase) for letter in range(letters)])

def _random_email(extension='edu', name=None):
    name = _random_name() if name is None else name
    return name + '@' + _random_name(5) + '.' + extension

