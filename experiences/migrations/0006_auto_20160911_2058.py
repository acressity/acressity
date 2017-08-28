# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('experiences', '0005_auto_20160911_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experience',
            name='author',
            field=models.ForeignKey(related_name='authored_experiences', to=settings.AUTH_USER_MODEL, help_text='\n            Explorer who created the experience. Has the ability of sending requests to other \n            explorers to become comrades in this experience.\n        '),
        ),
        migrations.AlterField(
            model_name='experience',
            name='brief',
            field=models.TextField(help_text='\n            Central to making this experience more real, write a brief about what \n            this experience entails. What are your hopes and aspirations? This \n            is a way for others to understand your intention and for you to get some clarity.\n        ', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='experience',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='\n            The day you committed to achieving this experience. Leave blank for today\n        ', blank=True),
        ),
        migrations.AlterField(
            model_name='experience',
            name='is_public',
            field=models.BooleanField(default=False, help_text="\n            It is recommended to keep an experience private until you are ready to \n            announce it to the world. Private experiences are only seen by its \n            explorers and those providing a correct password if one is selected, \n            so you can choose to share this experience with just a few people and \n            make it public later if you'd like.\n        "),
        ),
        migrations.AlterField(
            model_name='experience',
            name='password',
            field=models.CharField(help_text='\n            Submitting the correct password provides access to the \n            experience if it is private as well as all of the private narratives.\n        ', max_length=128, null=True, verbose_name='password', blank=True),
        ),
        migrations.AlterField(
            model_name='experience',
            name='percent_fulfilled',
            field=models.IntegerField(default=0, help_text="The fraction complete the experience is, from beginning\n        to end. Rough estimates are fine if there's no clear way to\n        determine this percentage", blank=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='experience',
            name='search_term',
            field=models.CharField(help_text="\n            Short phrase or word identifying the experience, allows access by typing \n            <code>http://acressity.com/your_search_term_here</code>. Needs to be \n            unique and cannot be the same as another explorer's trailname\n        ", max_length=80, unique=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='experience',
            name='status',
            field=models.CharField(help_text='Optional short state of the experience at the moment.', max_length=160, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='experience',
            name='title',
            field=models.CharField(help_text='Title of the experience.', max_length=255),
        ),
    ]
