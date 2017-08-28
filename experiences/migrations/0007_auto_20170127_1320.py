# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiences', '0006_auto_20160911_2058'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='experience',
            name='accepts_paypal',
        ),
        migrations.RemoveField(
            model_name='experience',
            name='donations',
        ),
    ]
