# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stripe_connect', '0003_auto_20170121_2141'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='charge',
            name='customer',
        ),
        migrations.AddField(
            model_name='charge',
            name='benefactor',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
