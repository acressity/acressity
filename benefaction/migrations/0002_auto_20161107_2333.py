# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benefaction', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='amount',
            field=models.DecimalField(help_text='\n            The price you deem appropriate for the propositioned addition to\n            the experience.\n        ', max_digits=9, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='bid',
            name='bounty',
            field=models.ForeignKey(related_name='bids', to='benefaction.Bounty', help_text='The bounty to which a series of bids/counter bids belong.'),
        ),
        migrations.AlterField(
            model_name='bid',
            name='is_accepted',
            field=models.BooleanField(default=False, help_text='\n            Accepting this bid will notify the bidder, directing them to completing\n            the payment. Many bids can be accepted, but only the first one to be\n            paid by a benefactor will be accepted, at which point the entire bounty\n            will be considered accepted.\n        '),
        ),
        migrations.AlterField(
            model_name='bid',
            name='proposition',
            field=models.CharField(help_text='\n            A proposition states what you would propose to add to this experience for the \n            proposed price. If this bid is accepted by a benefactor, you \n            would be held accountable for fulfilling this proposition as a part\n            of the experience.\n        ', max_length=512),
        ),
        migrations.AlterField(
            model_name='bounty',
            name='is_fulfilled',
            field=models.BooleanField(default=False, help_text="\n            True when the author of the campaign's experience\n            has successfully fulfilled the proposition and terms \n            of the bounty\n        "),
        ),
        migrations.AlterField(
            model_name='bounty',
            name='is_paid',
            field=models.BooleanField(default=False, help_text='\n            True when the payment from a benefactor\n            has successfully been made for a bid\n        '),
        ),
    ]
