# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benefaction', '0002_auto_20161107_2333'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bounty',
            name='is_paid',
        ),
        migrations.AddField(
            model_name='bid',
            name='is_paid',
            field=models.BooleanField(default=False, help_text='\n            True when the payment from a benefactor\n            has successfully been made for this bid\n        '),
        ),
    ]
