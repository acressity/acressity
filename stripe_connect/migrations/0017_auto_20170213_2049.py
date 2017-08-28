# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_connect', '0016_charge_stripe_account'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stripecustomer',
            name='explorer',
        ),
        migrations.AddField(
            model_name='stripeaccount',
            name='customer_id',
            field=models.CharField(default='cus_nonsense', max_length=255),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='StripeCustomer',
        ),
    ]
