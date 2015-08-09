# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('experiences', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Explorer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=60)),
                ('trailname', models.CharField(help_text='A trailname is a short username or nickname given to each explorer of this website, able to be changed at any time. Inspired by the tradition common with Appalachian Trail hikers, you\'re encouraged to create a trailname that describes an aspect of your journey at the moment.<br />It\'ll be displayed as John "<em>trailname</em>" Doe<br />It also allows others to find you by typing acressity.com/<em>trailname</em>', max_length=50, unique=True, null=True, blank=True)),
                ('brief', models.TextField(help_text='Short bio about you', null=True, blank=True)),
                ('email', models.EmailField(help_text='Email addresses are used for resetting passwords and notifications. Privacy is protected and confidential.', unique=True, max_length=254)),
                ('birthdate', models.DateField(null=True, blank=True)),
                ('date_joined', models.DateTimeField(default=datetime.datetime.now)),
                ('is_active', models.BooleanField(default=True)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('notify', models.BooleanField(default=True)),
                ('experiences', models.ManyToManyField(related_name='explorers', to='experiences.Experience')),
                ('featured_experience', models.ForeignKey(related_name='featured_experience', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='experiences.Experience', help_text="The experience that an explorer is currently featuring. Will be displayed on explorer's dash for easy accessibility and will be shown alongside explorer information for others to see.", null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
