# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experiences', '0002_auto_20160911_1443'),
        ('photologue', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='experience',
            name='gallery',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='photologue.Gallery'),
        ),
    ]
