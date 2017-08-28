# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benefaction', '0004_auto_20161109_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bounty',
            name='is_accepted',
            field=models.BooleanField(default=False, help_text='\n            Accepting this bounty will notify the creator, directing them to completing\n            the payment. It is a statement of accepting the terms by the explorer of the\n            experience, finalized by the payment to follow. Many bounties can be accepted.\n        '),
        ),
        migrations.AlterField(
            model_name='bounty',
            name='proposition',
            field=models.CharField(help_text='\n            A proposition states what you would propose to have added to the experience for the \n            proposed price. If this bounty is accepted and paid for by a benefactor, the \n            author of the experience would be held accountable for fulfilling this proposition \n            as a part of the experience.\n        ', max_length=512),
        ),
    ]
