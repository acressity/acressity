# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_connect', '0004_auto_20170121_2146'),
    ]

    operations = [
        migrations.RenameField(
            model_name='charge',
            old_name='refunded',
            new_name='is_refunded',
        ),
    ]
