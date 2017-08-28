# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('narratives', '0002_narrative_gallery'),
    ]

    operations = [
        migrations.AlterField(
            model_name='narrative',
            name='body',
            field=models.TextField(help_text='\n            The content of narrative. Where information regarding any thoughts, feelings, \n            updates, etc can be added.\n        '),
        ),
        migrations.AlterField(
            model_name='narrative',
            name='category',
            field=models.CharField(help_text='\n            Optional information used to classify and order the narratives within the experience.\n        ', max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='narrative',
            name='is_public',
            field=models.BooleanField(default=True, help_text="\n            Public narratives will be displayed in the default views. Private ones are \n            only seen by yourself and the other explorers in the narrative's experience. \n            Changing the status of the narrative also changes the status of the photo gallery.\n        "),
        ),
        migrations.AlterField(
            model_name='narrative',
            name='password',
            field=models.CharField(help_text='\n            Submitting the correct password provides access to this narrative if it is private.\n        ', max_length=128, null=True, verbose_name='password', blank=True),
        ),
        migrations.AlterField(
            model_name='narrative',
            name='title',
            field=models.CharField(help_text='\n            Title of the narrative. If none given, defaults to date created.\n        ', max_length=255, null=True, blank=True),
        ),
    ]
