# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benefaction', '0005_auto_20161113_2255'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='brief',
            field=models.TextField(help_text='\n            Optional description of the bounty detailing more\n            information, terms, or conditions regarding the proposition.\n        ', null=True, blank=True),
        ),
    ]
