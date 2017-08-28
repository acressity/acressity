# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('experiences', '0006_auto_20160911_2058'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('proposition', models.CharField(help_text='\n            What you would propose to add to this experience for the proposed\n            price. If this bid is accepted, the explorers of the experience\n            would be held accountable for fulfilling this proposition as a part\n            of the experience.\n        ', max_length=512)),
                ('amount', models.DecimalField(help_text='\n            The price you deem appropriate for the propositioned addition to\n            the experience\n        ', max_digits=9, decimal_places=2)),
                ('description', models.TextField(help_text='\n            Optional description of the bid detailing more\n            information, terms, or conditions regarding the proposition.\n        ', null=True, blank=True)),
                ('is_accepted', models.BooleanField(default=False, help_text='\n        Accepting this bid will notify the bidder, directing them to completing\n        the payment. Many bids can be accepted, but only the first one to be\n        paid by a benefactor will be accepted, at which point the entire bounty\n        will be considered accepted.\n        ')),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('bidder', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Bounty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_paid', models.BooleanField(default=False, help_text='True when the payment from a benefactor\n        has successfully been made for a bid')),
                ('is_fulfilled', models.BooleanField(default=False, help_text="True when the author of the campaign's experience\n        has successfully fulfilled the proposition and terms of the bounty")),
                ('date_created', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount_requested', models.DecimalField(help_text='\n            The total amount you need to set about achieving your experience. This\n            campaign is fulfilled once your benefactors have donated or funded\n            sufficient bounties to reach this amount, at which point it is time\n            to pursue the experience, making sure to fulfill the bounties during \n            the process.\n        ', max_digits=9, decimal_places=2, validators=[django.core.validators.MinValueValidator(25)])),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('experience', models.OneToOneField(to='experiences.Experience', help_text='\n            Become funded by benefactors to accomplish your experience. You have the\n            ability of hosting a bounty system where vicarious experience is auctioned\n            through bounties placed by both you and benefactors.\n        ')),
            ],
        ),
        migrations.AddField(
            model_name='bounty',
            name='campaign',
            field=models.ForeignKey(related_name='bounties', to='benefaction.Campaign', help_text=b''),
        ),
        migrations.AddField(
            model_name='bid',
            name='bounty',
            field=models.ForeignKey(related_name='bids', to='benefaction.Bounty', help_text='The bounty to which a series of bids/counter bids belong'),
        ),
    ]
