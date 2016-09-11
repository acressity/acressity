# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiences', '0004_auto_20160911_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experience',
            name='status',
            field=models.CharField(help_text='Optional short state of the experience at the moment.', max_length=200, null=True, blank=True),
        ),
    ]
