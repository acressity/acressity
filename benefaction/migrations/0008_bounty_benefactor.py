# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('benefaction', '0007_auto_20170107_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='bounty',
            name='benefactor',
            field=models.ForeignKey(related_name='benefactor_of', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
