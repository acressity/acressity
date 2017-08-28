# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_connect', '0008_stripeprofile_is_connected'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stripeprofile',
            name='is_connected',
        ),
    ]
