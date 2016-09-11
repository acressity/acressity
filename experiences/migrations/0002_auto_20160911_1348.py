# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ipn', '0007_auto_20160219_1135'),
        ('experiences', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='experience',
            name='author',
            field=models.ForeignKey(related_name='authored_experiences', to=settings.AUTH_USER_MODEL, help_text='Explorer who created the experience. Has the ability of sending requests to other explorers to become comrades in this experience.'),
        ),
        migrations.AddField(
            model_name='experience',
            name='benefactors',
            field=models.ManyToManyField(help_text='All those who have donated to this experience', related_name='benefactors', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='experience',
            name='donations',
            field=models.ManyToManyField(help_text='All the donations made to this experience', related_name='donations', to='ipn.PayPalIPN', blank=True),
        ),
    ]
