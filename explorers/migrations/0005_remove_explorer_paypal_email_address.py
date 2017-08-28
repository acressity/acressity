# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('explorers', '0004_auto_20161107_2333'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='explorer',
            name='paypal_email_address',
        ),
    ]
