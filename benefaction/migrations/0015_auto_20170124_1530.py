# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benefaction', '0014_auto_20170124_1529'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bounty',
            options={'ordering': ['-date_modified']},
        ),
    ]
