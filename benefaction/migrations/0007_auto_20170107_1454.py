# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benefaction', '0006_campaign_brief'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bounty',
            name='is_fulfilled',
            field=models.BooleanField(default=False, help_text="\n            A bounty is fulfilled when the author of the campaign's experience\n            has successfully fulfilled the proposition and terms of the bounty.\n        "),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='brief',
            field=models.TextField(help_text='\n            Optional description of the campaign detailing more information.\n        ', null=True, blank=True),
        ),
    ]
