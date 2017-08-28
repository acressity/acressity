# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_connect', '0015_remove_charge_stripe_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='charge',
            name='stripe_account',
            field=models.ForeignKey(default=1, to='stripe_connect.StripeAccount', help_text='\n            The connect account to which the payment was applied\n        '),
            preserve_default=False,
        ),
    ]
