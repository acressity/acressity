# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('explorers', '0002_auto_20160911_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='explorer',
            name='email',
            field=models.EmailField(help_text='Email addresses are used for resetting passwords and notifications. Privacy is protected and honored.', unique=True, max_length=254),
        ),
        migrations.AlterField(
            model_name='explorer',
            name='trailname',
            field=models.CharField(help_text='\n            A trailname is a short username or nickname given to each \n            explorer of this website, able to be changed at any time. Inspired \n            by the tradition common with Appalachian Trail hikers, you\'re \n            encouraged to create a trailname that describes an aspect of your \n            journey at the moment.<br />It\'ll be displayed as John "<em>trailname</em>" \n            Doe<br />It also allows others to find you by typing \n            <code>acressity.com/<em>trailname</em></code>\n        ', max_length=55, unique=True, null=True, blank=True),
        ),
    ]
