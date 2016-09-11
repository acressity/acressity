# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('experiences', '0002_auto_20160911_1348'),
    ]

    operations = [
        migrations.CreateModel(
            name='Narrative',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField(help_text='The content of narrative. Where information regarding any thoughts, feelings, updates, etc can be added.')),
                ('title', models.CharField(help_text='Title of the narrative. If none given, defaults to date created.', max_length=255, null=True, blank=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, blank=True)),
                ('date_modified', models.DateTimeField(help_text=b'Updated every time object is saved', auto_now=True)),
                ('category', models.CharField(help_text=b'Optional information used to classify and order the narratives within the experience.', max_length=50, null=True, blank=True)),
                ('is_public', models.BooleanField(default=True, help_text=b"Public narratives will be displayed in the default views. Private ones are only seen by yourself and the other explorers in the narrative's experience. Changing the status of the narrative also changes the status of the photo gallery.")),
                ('password', models.CharField(help_text='Submitting the correct password provides access to this narrative if it is private.', max_length=128, null=True, verbose_name='password', blank=True)),
                ('author', models.ForeignKey(related_name='narratives', to=settings.AUTH_USER_MODEL)),
                ('experience', models.ForeignKey(related_name='narratives', to='experiences.Experience')),
            ],
            options={
                'get_latest_by': 'date_created',
            },
        ),
    ]
