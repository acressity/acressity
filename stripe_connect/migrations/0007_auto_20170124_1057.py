# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_connect', '0006_charge_date_created'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='charge',
            options={'get_latest_by': 'date_created'},
        ),
    ]
