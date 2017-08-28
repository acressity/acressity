# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stripe_connect', '0010_stripeprofile_is_deauthorized'),
    ]

    operations = [
        migrations.CreateModel(
            name='StripeAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('account_id', models.CharField(max_length=255)),
                ('access_token', models.CharField(max_length=255)),
                ('refresh_token', models.CharField(max_length=255)),
                ('token_type', models.CharField(max_length=255)),
                ('stripe_publishable_key', models.CharField(max_length=255)),
                ('scope', models.CharField(max_length=255)),
                ('livemode', models.BooleanField(default=False)),
                ('is_deauthorized', models.BooleanField(default=False)),
                ('explorer', models.OneToOneField(related_name='stripe_account', to=settings.AUTH_USER_MODEL, help_text='\n            The explorer to whom the account belongs.\n        ')),
            ],
        ),
        migrations.CreateModel(
            name='StripeCustomer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('customer_id', models.CharField(max_length=255)),
                ('explorer', models.OneToOneField(related_name='stripe_customer', to=settings.AUTH_USER_MODEL, help_text='\n            The explorer represented by the customer.\n        ')),
            ],
        ),
        migrations.RemoveField(
            model_name='stripeprofile',
            name='explorer',
        ),
        migrations.RemoveField(
            model_name='charge',
            name='stripe_profile',
        ),
        migrations.AlterField(
            model_name='charge',
            name='benefactor',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.DeleteModel(
            name='StripeProfile',
        ),
        migrations.AddField(
            model_name='charge',
            name='stripe_account',
            field=models.ForeignKey(default=1, to='stripe_connect.StripeAccount', help_text='\n            The connect account to which the payment was applied\n        '),
            preserve_default=False,
        ),
    ]
