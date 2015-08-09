# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('experiences', '0003_experience_gallery'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cheer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_cheered', models.DateTimeField(default=datetime.datetime.now)),
                ('cheerer', models.ForeignKey(related_name='cheers_from', to=settings.AUTH_USER_MODEL)),
                ('explorer', models.ForeignKey(related_name='cheers_for', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Hurrah',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_pk', models.TextField(verbose_name='object ID')),
                ('content_type', models.ForeignKey(related_name='content_type_set_for_hurrah', verbose_name='content type', to='contenttypes.ContentType')),
                ('explorer', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='InvitationRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(default=datetime.datetime.now)),
                ('code', models.CharField(help_text=b'Random code sent with the email in the url, used to confirm the uniqueness and identity of the invited explorer.', max_length=25, null=True, blank=True)),
                ('author', models.ForeignKey(related_name='experience_author', to=settings.AUTH_USER_MODEL, help_text=b'The author of the experience. Able to be the explorer who invited the recruit or potential explorer, or the person who an existing explorer is contacting to become a part of the experience.')),
                ('experience', models.ForeignKey(to='experiences.Experience')),
            ],
        ),
        migrations.CreateModel(
            name='PotentialExplorer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('email', models.EmailField(help_text=b'This information is used responsibly. It will only be used to send an invitation request.', max_length=254)),
            ],
        ),
        migrations.AddField(
            model_name='invitationrequest',
            name='potential_explorer',
            field=models.ForeignKey(related_name='invitation_request', blank=True, to='support.PotentialExplorer', help_text=b'References potential new user with little information for registration provided by invitation author.', null=True),
        ),
        migrations.AddField(
            model_name='invitationrequest',
            name='recruit',
            field=models.ForeignKey(related_name='experience_recruit', blank=True, to=settings.AUTH_USER_MODEL, help_text=b'References an existing explorer potentially being added to experience.', null=True),
        ),
    ]
