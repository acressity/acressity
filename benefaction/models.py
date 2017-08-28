from decimal import Decimal

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Sum, F
from django.db.backends.utils import format_number
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from experiences.models import Experience
from stripe_connect.models import Charge


class Campaign(models.Model):
    help_text=_('''
        A campaign helps an otherwise out-of-reach experience on a bucketlist become funded by benefactors. 
        The core of the campaign are bounties, which can be created both by the
        author of the campaign's experience and potential benefactors.
        Bounties are set to auction aspects of the experience, encouraging funding by giving potential
        benefactors the opportunity of having vicarious experience through those
        living their dreams by pursuing the experience (example: the proposition "Name the Bike" 
        for $100 for the experience of "Biking Across America"). 
        Bounties can be accepted, countered with new bounties, or ignored. They are not
        accepted until both the author of the experience and a benefactor both
        agree on a bounty which specifies the proposition, a financial amount/reward, 
        and a description of terms/conditions, at which point a payment can be
        processed. Recipient of funds will be the author of the experience, who
        then has the responsibility of fulfilling the propositions of each bounty
        while pursuing the campaign's experience.
    ''')

    experience = models.OneToOneField(
        Experience,
        help_text=_('''
            Become funded by benefactors to accomplish your experience. You have the
            ability of hosting a bounty system where vicarious experience is auctioned
            through bounties placed by both you and potential benefactors.
        ''')
    )
    amount_requested = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        null=False,
        blank=False,
        validators=[MinValueValidator(25)],
        help_text=_('''
            The total amount you need to set about achieving your experience. This
            campaign is fulfilled once your benefactors have donated or funded
            sufficient bounties to reach this amount, at which point it is time
            to pursue the experience, making sure to fulfill the bounties during 
            the process.
        ''')
    )
    brief = models.TextField(
        help_text=_('''
            Optional description of the campaign detailing more information.
        '''),
        null=True,
        blank=True
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return 'Benefaction campaign for {0}'.format(self.experience)

    def __str__(self):
        return self.__unicode__()

    def model(self):
        return self.__class__.__name__

    def get_absolute_url(self):
        return reverse('campaign', args=[self.pk])

    def get_recipient(self):
        return self.experience.author

    def get_first_level(self):
        return self.bounties.filter(parent=None)

    def get_amount_raised(self):
        return Decimal(
            format_number(
                sum([
                    bounty.get_charge().amount_in_cents for bounty in self.bounties.all() \
                        if bounty.has_charge() and not bounty.get_charge().is_refunded
                ]) / 100.0,
                None, 2
            )
        ) or Decimal(format_number(0, None, 0))

    def get_percent_raised(self):
        return min(100.0, (self.get_amount_raised() / self.amount_requested) * 100)

    def is_complete(self):
        return self.get_amount_raised() >= self.amount_requested

    def can_access(self, explorer, cookie):
        return self.experience.can_access(explorer, cookie)


class Bounty(models.Model):
    help_text=_('''
        A bounty is a way to auction aspects of an experience, encouraging funding by giving potential
        benefactors the opportunity of having vicarious experience through those
        fulfilling their dreams by pursuing the experience.
        It includes a proposition and a reward for fulfilling the proposition (example: the 
        proposition "Name the Bike" for $100 for the experience of "Biking Across America"). 
        Bounties can be set by the experience's explorer
        or by potential benefactors. They can be countered to reach a point desireable by both,
        at which point the payment can be made. The recipient of the funds (the experience's explorer)
        is then responsible for fulfilling the proposition of the bounty while pursuing the experience.
    ''')
    campaign = models.ForeignKey(
        Campaign,
        related_name='bounties',
        help_text=''''''
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        help_text=_('''
            The bounty being countered with new proposition/amount/terms by this one.
        ''')
    )
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    benefactor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, # Allows for anonymous benefaction
        blank=True,
        related_name='bounties_benefactor'
    )
    is_fulfilled = models.BooleanField(
        default=False,
        blank=True,
        help_text=_('''
            A bounty is fulfilled when the author of the campaign's experience
            has successfully fulfilled the proposition and terms of the bounty.
        ''')
    )
    proposition = models.CharField(
        max_length=512, 
        null=False,
        blank=False,
        help_text=_('''
            A proposition states what you would propose to have added to the experience for the 
            proposed price. If this bounty is accepted and paid for by a benefactor, the 
            author of the experience would be held accountable for fulfilling this proposition 
            as a part of the experience.
        ''')
    )
    amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        null=False,
        blank=False,
        help_text=_('''
            The price you deem appropriate for the propositioned addition to
            the experience.
        ''')
    )
    description = models.TextField(
        help_text=_('''
            Optional description of the bounty detailing more
            information, terms, or conditions regarding the proposition.
        '''),
        null=True,
        blank=True
    )
    is_accepted = models.BooleanField(
        default=False,
        null=False,
        help_text=_('''
            Accepting this bounty will notify the creator, directing them to completing
            the payment. It is a statement of accepting the terms by the explorer of the
            experience, finalized by the payment to follow. Many bounties can be accepted.
        ''')
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_modified']

    def __unicode__(self):
        return self.proposition

    def model(self):
        return self.__class__.__name__

    def get_absolute_url(self):
        return reverse('bounty', args=[self.pk])

    def get_recipient(self):
        return self.campaign.get_recipient()

    def get_benefactor(self):
        try:
            return self.get_charge().benefactor
        except ObjectDoesNotExist:
            return None

    def is_paid(self):
        return self.has_charge() and \
            not self.get_charge().is_refunded and \
            self.get_charge().amount_in_cents / Decimal(100) >= self.amount

    def payable(self):
        return not self.campaign.is_complete() and not self.is_paid()

    def charges(self):
        return Charge.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_pk=self.pk
        )

    def get_charge(self):
        # The most recent charge; the current one
        if not self.has_charge():
            return None
        return self.charges().order_by('-date_created')[0]

    def has_charge(self):
        return Charge.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_pk=self.pk
        ).exists()

    def get_children(self):
        return Bounty.objects.filter(parent=self)

    def has_children(self):
        return self.get_children().exists()

    def get_level(self):
        if self.parent is None:
            return 0
        return 1 + self.parent.get_level()

    def deletable(self):
        return not self.is_paid() and not self.has_children()

    def editable(self):
        return self.deletable()

    def can_access(self, explorer, cookie):
        return self.campaign.can_access(explorer, cookie) or self.get_benefactor() == explorer

