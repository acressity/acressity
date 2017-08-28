# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benefaction', '0011_remove_bounty_is_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='bounty',
            name='is_paid',
            field=models.BooleanField(default=False, help_text='\n            True when the payment from a benefactor has successfully been made for this bounty\n        '),
        ),
    ]
