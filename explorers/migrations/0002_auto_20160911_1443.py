# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experiences', '0003_experience_gallery'),
        ('explorers', '0001_initial'),
        ('photologue', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='explorer',
            name='gallery',
            field=models.OneToOneField(related_name='story_gallery', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='photologue.Gallery'),
        ),
        migrations.AddField(
            model_name='explorer',
            name='tracking_experiences',
            field=models.ManyToManyField(help_text='Experiences that the explorer has chosen to track.', related_name='tracking_explorers', to='experiences.Experience', blank=True),
        ),
    ]
