import requests
import stripe

from rauth import OAuth2Service

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.sites.models import Site
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.contenttypes.models import ContentType


stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeAccount(models.Model):
    help_text=_('''
        Stripe is a payment provider which grants you the ability of creating an
        account to receive and offer payments. Creating an account is simple and
        takes place on their secure servers. Payments and credit card processing is
        also handled entirely on Stripe's secure servers. Authorizing Acressity to access this
        account will allow you to receive payments from benefactors and make
        contributions to others so you yourself can become the benefactor of
        another's journey. Stripe charges a flat fee of 2.9% + 30 cents which is deducted from the
        original contribution made by the benefactor. Acressity also charges a
        service fee of {acressity_fee}% in addition to this figure. These fees do not increase
        the amount charged of the benefactor and are less than those encountered on 
        Kickstarter and GoFundMe. Stripe is one way in which you can
        break past financial obstacles keeping you from accomplishing your dreams
        or a way in which you can assist others in overcoming their financial
        limitations.
    '''.format(acressity_fee=settings.ACRESSITY_SERVICE_PERCENTAGE))

    stripe_dashboard_url = settings.STRIPE_DASHBOARD_URL

    explorer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='stripe_account',
        help_text=_('''
            The explorer to whom the account belongs.
        ''')
    )
    account_id = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    customer_id = models.CharField(max_length=255, null=True)
    token_type = models.CharField(max_length=255)
    stripe_publishable_key = models.CharField(max_length=255)
    scope = models.CharField(max_length=255)
    livemode = models.BooleanField(default=False)
    is_deauthorized = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def fetch_stripe_is_connected(self):
        # Ping Stripe to see if the account is actively connected
        # To be done right before making payment
        try:
            return bool(self.fetch_stripe_account())
        except stripe.error.PermissionError:
            return False

    def fetch_stripe_account(self):
        return stripe.Account.retrieve(
            self.account_id
        )

    def fetch_stripe_charges_enabled(self):
        return self.fetch_stripe_account().charges_enabled

    def fetch_customer(self):
        return stripe.Customer.retrieve(
            self.customer_id
        )

    def fetch_has_source(self):
        return bool(self.fetch_customer().sources.get('total_count'))

    @classmethod
    def connect_oauth_service(cls):
        return OAuth2Service(
            name='stripe',
            client_id=settings.STRIPE_CLIENT_ID,
            client_secret=settings.STRIPE_SECRET_KEY,
            authorize_url=settings.STRIPE_AUTHORIZE_URL,
            access_token_url=settings.STRIPE_ACCESS_TOKEN_URL,
            base_url=settings.STRIPE_BASE_URL
        )

    def disconnect_account(self):
        data = {
            'client_secret': settings.STRIPE_SECRET_KEY,
            'client_id': settings.STRIPE_CLIENT_ID,
            'stripe_user_id': self.account_id,
        }

        response = requests.post(settings.STRIPE_DEAUTHORIZE_URL, data=data)
        if response.ok:
            if response.json().get('stripe_user_id') == self.account_id:
                self.is_deauthorized = True
                self.save()
            else:
                raise stripe.error.AuthenticationError
        else:
            raise stripe.error.APIError

    @classmethod
    def gen_auth_url_explorer(cls, explorer):
        # Build url to which the explorer will be sent to create Stripe
        # and/or authorize Acressity to use their account
        # It includes parameters for pre-filling form fields
        explorer_url = settings.SCHEME + '://' + Site.objects.get_current().domain + explorer.get_absolute_url()
        params = {
            'response_type': 'code',
            'scope': 'read_write',
            'stripe_user[first_name]': explorer.first_name,
            'stripe_user[last_name]': explorer.last_name,
            'stripe_user[email]': explorer.email,
            'stripe_user[url]': explorer_url,
            'stripe_user[physical_product]': False,
            'stripe_user[product_description]': _('''Payments received will go towards funding the pursuit of an experience on a bucketlist.'''),
        }
        return cls.connect_oauth_service().get_authorize_url(**params)

    @classmethod
    def generate_authorize_url(cls):
        # Build url to which the user will be sent to create Stripe
        # and/or authorize Acressity to use their account
        params = {
            'response_type': 'code',
            'scope': 'read_write',
        }
        return cls.connect_oauth_service().get_authorize_url(**params)

    @classmethod
    def to_cents(cls, amount):
        return int(amount * 100)

    @classmethod
    def calc_app_fee_cents(cls, amount):
        return int(cls.to_cents(amount) * (settings.ACRESSITY_SERVICE_PERCENTAGE / 100.0))


class Charge(models.Model):
    charge_id = models.CharField(max_length=255)
    stripe_account = models.ForeignKey(
        StripeAccount,
        help_text=_('''
            The connect account to which the payment was applied
        ''')
    )
    amount_in_cents = models.IntegerField()
    is_refunded = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_pk = models.TextField(_('object ID'), null=False)
    benefactor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True
    )
    date_created = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'date_created'

    def fetch_stripe_charge(self):
        # Get object with more data from Stripe
        return stripe.Charge.retrieve(
            self.charge_id,
            stripe_account=self.stripe_account.account_id
        )

