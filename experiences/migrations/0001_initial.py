# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('experience', models.CharField(help_text='Title of the experience.', max_length=200)),
                ('date_created', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('date_modified', models.DateTimeField(help_text='Updated every time object saved', auto_now=True, null=True)),
                ('brief', models.TextField(help_text='Written description of the experience to provide a little insight.', null=True, blank=True)),
                ('status', models.CharField(help_text='Optional short state of the experience at the moment.', max_length=160, null=True, blank=True)),
                ('is_public', models.BooleanField(default=True, help_text="Changing public and private status is only available to the experience's author. Private experiences are only seen by its explorers and those providing a correct password if one is selected. A correct password also provides access to all private narratives. Making an experience private will also set all of it's narratives to being private. Changing the status of the experience changes the status of the experience's gallery. However, private narratives do not become public when the experience is changed from private to public.")),
                ('password', models.CharField(help_text='Submitting the correct password provides access to the experience if it is private as well as all of the private narratives.', max_length=128, null=True, verbose_name='password', blank=True)),
                ('search_term', models.CharField(help_text="Short phrase or word identifying the experience, allows access by typing http://acressity.com/your_search_term_here. Needs to be unique and cannot be the same as another explorer's trailname", max_length=80, unique=True, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='FeaturedExperience',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_featured', models.DateTimeField(default=datetime.datetime.now)),
                ('experience', models.ForeignKey(to='experiences.Experience')),
            ],
        ),
    ]
