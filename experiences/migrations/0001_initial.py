# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text='Title of the experience.', max_length=255)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, help_text='The day you committed to achieving this\n                experience. Leave blank for today', blank=True)),
                ('date_modified', models.DateTimeField(help_text='Updated every time object saved', auto_now=True, null=True)),
                ('brief', models.TextField(help_text='Central to making this experience more real, write a brief about what this experience entails. What are your hopes and aspirations? This is a way for others to understand your intention and for you to get some clarity.', null=True, blank=True)),
                ('status', models.CharField(help_text='Optional short state of the experience at the moment.', max_length=160, null=True, blank=True)),
                ('is_public', models.BooleanField(default=False, help_text="It is recommended to keep an experience private until you are ready to announce it to the world. Private experiences are only seen by its explorers and those providing a correct password if one is selected, so you can choose to share this experience with just a few people and make it public later if you'd like.")),
                ('percent_fulfilled', models.IntegerField(default=0, help_text="The fraction complete the experience is, from beginning\n            to end. Rough estimates are fine if there's no clear way to\n            determine this percentage", blank=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('password', models.CharField(help_text='Submitting the correct password provides access to the experience if it is private as well as all of the private narratives.', max_length=128, null=True, verbose_name='password', blank=True)),
                ('search_term', models.CharField(help_text="Short phrase or word identifying the experience, allows access by typing <code>http://acressity.com/your_search_term_here</code>. Needs to be unique and cannot be the same as another explorer's trailname", max_length=80, unique=True, null=True, blank=True)),
                ('accepts_paypal', models.BooleanField(default=False, help_text='Check this box if you want to be able to accept PayPal donations from benefactors.')),
                ('intended_completion_date', models.DateField(help_text='Optional date by which you intend to be\n                finished. Take care if choosing to set a date, as this feature\n                can be demotivating if used improperly. Leave blank if you do\n                not want this to be displayed or if not relevant.', null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='FeaturedExperience',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_featured', models.DateTimeField(default=django.utils.timezone.now)),
                ('experience', models.ForeignKey(to='experiences.Experience')),
            ],
        ),
    ]
