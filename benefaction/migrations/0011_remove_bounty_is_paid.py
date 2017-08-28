# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benefaction', '0010_auto_20170119_1430'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bounty',
            name='is_paid',
        ),
    ]
