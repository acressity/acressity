# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_connect', '0014_auto_20170213_1553'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='charge',
            name='stripe_account',
        ),
    ]
