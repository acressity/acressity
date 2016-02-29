from django.contrib.auth.hashers import make_password

from explorers.models import Explorer


def new_explorer():
    return Explorer.objects.create(first_name='Dwain',
                                   last_name='Dedrick',
                                   trailname='MachuPikchu',
                                   password=make_password('D0N_QU!X0TE_5'),
                                   email='dwain@somewhere.edu',
                                   is_superuser=True)
