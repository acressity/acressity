# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('benefaction', '0013_remove_bounty_is_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='bounty',
            name='date_modified',
            field=models.DateTimeField(default=datetime.datetime(2017, 1, 24, 15, 29, 39, 420235), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='campaign',
            name='date_modified',
            field=models.DateTimeField(default=datetime.datetime(2017, 1, 24, 15, 29, 50, 223760), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bounty',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
