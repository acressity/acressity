# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_connect', '0009_remove_stripeprofile_is_connected'),
    ]

    operations = [
        migrations.AddField(
            model_name='stripeprofile',
            name='is_deauthorized',
            field=models.BooleanField(default=False),
        ),
    ]
