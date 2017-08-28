# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stripe_connect', '0002_stripeprofile_customer_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='charge',
            name='bounty',
        ),
        migrations.AddField(
            model_name='charge',
            name='content_type',
            field=models.ForeignKey(related_name='content_type_set_for_charge', default=1, verbose_name='content type', to='contenttypes.ContentType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='charge',
            name='customer',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='charge',
            name='object_pk',
            field=models.TextField(default=1, verbose_name='object ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='charge',
            name='stripe_profile',
            field=models.ForeignKey(help_text='\n            The connect account to which the payment was applied\n        ', to='stripe_connect.StripeProfile'),
        ),
    ]
