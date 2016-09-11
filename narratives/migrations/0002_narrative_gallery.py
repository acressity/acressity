# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('narratives', '0001_initial'),
        ('photologue', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='narrative',
            name='gallery',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='photologue.Gallery'),
        ),
    ]
