# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_connect', '0017_auto_20170213_2049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stripeaccount',
            name='customer_id',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
