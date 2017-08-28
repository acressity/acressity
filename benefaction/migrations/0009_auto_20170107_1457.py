# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('benefaction', '0008_bounty_benefactor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bounty',
            name='benefactor',
            field=models.ForeignKey(related_name='bounties_benefactor', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
