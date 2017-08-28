# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('benefaction', '0003_auto_20161107_2339'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bid',
            name='bidder',
        ),
        migrations.RemoveField(
            model_name='bid',
            name='bounty',
        ),
        migrations.AddField(
            model_name='bounty',
            name='amount',
            field=models.DecimalField(default=0, help_text='\n            The price you deem appropriate for the propositioned addition to\n            the experience.\n        ', max_digits=9, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bounty',
            name='creator',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bounty',
            name='description',
            field=models.TextField(help_text='\n            Optional description of the bounty detailing more\n            information, terms, or conditions regarding the proposition.\n        ', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bounty',
            name='is_accepted',
            field=models.BooleanField(default=False, help_text='\n            Accepting this bounty will notify the creator, directing them to completing\n            the payment. Many bids can be accepted, but only the first one to be\n            paid by a benefactor will be accepted.\n        '),
        ),
        migrations.AddField(
            model_name='bounty',
            name='is_paid',
            field=models.BooleanField(default=False, help_text='\n            True when the payment from a benefactor has successfully been made for this bounty\n        '),
        ),
        migrations.AddField(
            model_name='bounty',
            name='parent',
            field=models.ForeignKey(blank=True, to='benefaction.Bounty', help_text='\n            The bounty being countered with new proposition/amount/terms by this one.\n        ', null=True),
        ),
        migrations.AddField(
            model_name='bounty',
            name='proposition',
            field=models.CharField(default='Go to the park', help_text='\n            A proposition states what you would propose to have added to the experience for the \n            proposed price. If this bid is accepted and paid for by a benefactor, the \n            author of the experience would be held accountable for fulfilling this proposition \n            as a part of the experience.\n        ', max_length=512),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bounty',
            name='is_fulfilled',
            field=models.BooleanField(default=False, help_text="\n            A bounty is fulfilled when the author of the campaign's experience\n            has successfully fulfilled the proposition and terms \n            of the bounty.\n        "),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='experience',
            field=models.OneToOneField(to='experiences.Experience', help_text='\n            Become funded by benefactors to accomplish your experience. You have the\n            ability of hosting a bounty system where vicarious experience is auctioned\n            through bounties placed by both you and potential benefactors.\n        '),
        ),
        migrations.DeleteModel(
            name='Bid',
        ),
    ]
