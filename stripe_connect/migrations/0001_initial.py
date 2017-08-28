# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('benefaction', '0010_auto_20170119_1430'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('charge_id', models.CharField(max_length=255)),
                ('amount_in_cents', models.IntegerField()),
                ('refunded', models.BooleanField(default=False)),
                ('bounty', models.ForeignKey(to='benefaction.Bounty')),
            ],
        ),
        migrations.CreateModel(
            name='StripeProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('account_id', models.CharField(max_length=255)),
                ('access_token', models.CharField(max_length=255)),
                ('refresh_token', models.CharField(max_length=255)),
                ('token_type', models.CharField(max_length=255)),
                ('stripe_publishable_key', models.CharField(max_length=255)),
                ('scope', models.CharField(max_length=255)),
                ('livemode', models.BooleanField(default=False)),
                ('explorer', models.OneToOneField(related_name='stripe_profile', to=settings.AUTH_USER_MODEL, help_text='\n            The user to whom the account belongs.\n        ')),
            ],
        ),
        migrations.AddField(
            model_name='charge',
            name='stripe_profile',
            field=models.ForeignKey(to='stripe_connect.StripeProfile'),
        ),
    ]
