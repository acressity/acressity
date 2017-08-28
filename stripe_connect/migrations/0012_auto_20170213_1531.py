# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_connect', '0011_auto_20170213_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stripeaccount',
            name='account_id',
            field=models.CharField(max_length=254),
        ),
    ]
