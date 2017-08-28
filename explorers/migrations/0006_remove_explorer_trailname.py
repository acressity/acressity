# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('explorers', '0005_remove_explorer_paypal_email_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='explorer',
            name='trailname',
        ),
    ]
