# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('explorers', '0006_remove_explorer_trailname'),
    ]

    operations = [
        migrations.AddField(
            model_name='explorer',
            name='trailname',
            field=models.CharField(help_text='\n            A trailname is an optional short username or nickname for the \n            explorers of this website, able to be changed at any time. Inspired \n            by the tradition common with Appalachian Trail hikers, you\'re \n            encouraged to create a trailname that describes an aspect of your \n            journey at the moment.<br />It\'ll be displayed as John "<em>trailname</em>" \n            Doe.<br />It also allows others to find you by typing \n            <code>http://localhost:8000/<em>trailname</em></code>.\n        ', max_length=55, unique=True, null=True, blank=True),
        ),
    ]
