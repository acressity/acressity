# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_connect', '0007_auto_20170124_1057'),
    ]

    operations = [
        migrations.AddField(
            model_name='stripeprofile',
            name='is_connected',
            field=models.BooleanField(default=True),
        ),
    ]
