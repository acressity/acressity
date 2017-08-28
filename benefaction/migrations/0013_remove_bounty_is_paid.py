# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benefaction', '0012_bounty_is_paid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bounty',
            name='is_paid',
        ),
    ]
