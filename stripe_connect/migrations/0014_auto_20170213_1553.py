# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.datetime_safe


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_connect', '0013_auto_20170213_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='stripeaccount',
            name='date_created',
            field=models.DateTimeField(default=django.utils.datetime_safe.datetime.now, auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stripeaccount',
            name='date_modified',
            field=models.DateTimeField(default=django.utils.datetime_safe.datetime.now, auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stripecustomer',
            name='date_created',
            field=models.DateTimeField(default=django.utils.datetime_safe.datetime.now, auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stripecustomer',
            name='date_modified',
            field=models.DateTimeField(default=django.utils.datetime_safe.datetime.now, auto_now=True),
            preserve_default=False,
        ),
    ]
