# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiences', '0003_experience_gallery'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experience',
            name='title',
            field=models.CharField(help_text='Title of the experience.', max_length=200),
        ),
    ]
