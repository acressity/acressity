# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_connect', '0005_auto_20170123_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='charge',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2017, 1, 23, 14, 39, 18, 826683), auto_now=True),
            preserve_default=False,
        ),
    ]
