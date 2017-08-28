import stripe 
import mock
import requests

from django.test import TestCase, RequestFactory, TransactionTestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from stripe.resource import convert_to_stripe_object
from stripe.error import InvalidRequestError

from stripe_connect.models import StripeAccount, Charge
from explorers.tests import helpers as explorer_helpers
from experiences.models import Experience
from benefaction.models import Campaign, Bounty

from stripe_connect.tests.test_main import StripeTestCase
from stripe_connect.tests.mocks.mock_token import MockToken
from stripe_connect.tests.mocks.mock_customer import MockCustomer
from stripe_connect.tests.mocks.mock_account import MockAccount
from stripe_connect.tests.mocks.mock_charge import MockCharge


stripe.api_key = settings.STRIPE_SECRET_KEY


@mock.patch('stripe.Customer', MockCustomer)
@mock.patch('stripe.Token', MockToken)
@mock.patch('stripe.Account', MockAccount)
@mock.patch('stripe.Charge', MockCharge)
class StripeTestDisconnect(StripeTestCase):
    @mock.patch('requests.post')
    def test_explorer_can_disconnect_own_account(self, requests_post):
        self.client.login(
            username=self.explorer_benefactor_authorized.email,
            password=self.explorer_benefactor_authorized.password_unhashed
        )

        requests_post.return_value.ok = True
        requests_post.return_value.json.return_value = {
            'stripe_user_id': self.explorer_benefactor_authorized.stripe_account.account_id,
        }

        self.assertFalse(
            self.explorer_benefactor_authorized.stripe_account.is_deauthorized
        )

        response = self.client.post(
            reverse(
                'stripe_connect.disconnect',
                args=[self.explorer_benefactor_authorized.stripe_account.pk]
            )
        )
        self.explorer_benefactor_authorized.stripe_account.refresh_from_db()

        self.assertTrue(
            self.explorer_benefactor_authorized.stripe_account.is_deauthorized
        )
        self.assertEqual(response.status_code, 302)

    def test_explorer_cannot_disconnect_anothers_account(self):
        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )

        response = self.client.post(
            reverse(
                'stripe_connect.disconnect',
                args=[self.explorer_benefactor_authorized.stripe_account.pk]
            )
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            self.explorer_benefactor_authorized.stripe_account.is_deauthorized
        )

