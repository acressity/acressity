import stripe 
import mock

from django.test import TestCase, RequestFactory, TransactionTestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from stripe_connect.models import StripeAccount, Charge
from explorers.tests import helpers as explorer_helpers
from experiences.models import Experience
from benefaction.models import Campaign, Bounty

from stripe_connect.tests.mocks.mock_token import MockToken
from stripe_connect.tests.mocks.mock_customer import MockCustomer
from stripe_connect.tests.mocks.mock_account import MockAccount
from stripe_connect.tests.mocks.mock_charge import MockCharge

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeTestCase(TestCase):
    def setUp(self):
        self.explorer_author_authorized = explorer_helpers.create_test_explorer_superuser()
        self.explorer_benefactor_authorized = explorer_helpers.create_test_explorer()
        self.explorer_other = explorer_helpers.create_test_explorer()

        stripe_account_author = StripeAccount.objects.create(
            explorer=self.explorer_author_authorized,
            account_id=MockAccount.account_data[0].get('id'),
            customer_id=MockCustomer.customer_data[0].get('id'),
            access_token='pt_nonsense',
            refresh_token='rt_nonsense',
            token_type='bearer',
            stripe_publishable_key='pk_nonsense',
            scope='read_write',
            livemode=False,
            is_deauthorized=False
        )

        stripe_account_benefactor = StripeAccount.objects.create(
            explorer=self.explorer_benefactor_authorized,
            account_id=MockAccount.account_data[1].get('id'),
            customer_id=MockCustomer.customer_data[1].get('id'),
            access_token='pt_nonsense',
            refresh_token='rt_nonsense',
            token_type='bearer',
            stripe_publishable_key='pk_nonsense',
            scope='read_write',
            livemode=False,
            is_deauthorized=False
        )

        self.campaign_experience = Experience.objects.create(
            title='Go Skydiving',
            author=self.explorer_author_authorized,
            is_public=True
        )

        self.campaign = Campaign.objects.create(
            experience=self.campaign_experience,
            amount_requested=600.00
        )

        self.bounty_by_author = Bounty.objects.create(
            campaign=self.campaign,
            creator=self.explorer_author_authorized,
            proposition='You get to join me',
            amount=1000,
            description='Bring yourself along for the experience. Make sure to bring your camera to capture the facial expression of utter trepidation'
        )
