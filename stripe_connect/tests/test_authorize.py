import stripe 
import mock

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
class StripeTestAuthorize(StripeTestCase):
    def test_connected_explorer_cannot_reauthorize(self):
        self.client.login(
            username=self.explorer_benefactor_authorized.email,
            password=self.explorer_benefactor_authorized.password_unhashed)

        response = self.client.get(
            reverse('stripe_connect.authorize'))

        self.assertEqual(response.status_code, 403)

        response = self.client.post(
            reverse('stripe_connect.authorize'))

        self.assertEqual(response.status_code, 403)

    def test_connected_explorer_cannot_reauthorize_from_response(self):
        self.client.login(
            username=self.explorer_benefactor_authorized.email,
            password=self.explorer_benefactor_authorized.password_unhashed)

        response = self.client.get(
            reverse('stripe_connect.response'))

        self.assertEqual(response.status_code, 403)

    @mock.patch('rauth.OAuth2Service.get_raw_access_token')
    def test_receiving_token_from_code_creates_account(self, get_raw_access_token):
        # The code stripe will have returned from Oauth2 request
        valid_test_code = 'ac_A0mr8dx9WSmrMDznoVWHGLo6o8C5dq5E'

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed)

        # The data received from stripe after code submission
        access_token_data = {
            'stripe_publishable_key': 'pk_test_HTBqs2fQvrzYAvBRfrQqDtxZ',
            'access_token': 'sk_test_8BRNaZjmk6PQf3cL3uZXxnig',
            'livemode': False,
            'token_type': 'bearer',
            'scope': u'read_write',
            'refresh_token': 'rt_A0mvylp7dtx1d1qkolkdfgx4kDYf2snPisVsiHDmU0CCRksQ',
            'stripe_user_id': u'acct_19eBR1EdIW29EyUP'
        }
        get_raw_access_token.return_value.json.return_value = access_token_data

        response = self.client.get(
            reverse('stripe_connect.response'),
            {'code': valid_test_code})

        self.assertEqual(get_raw_access_token.call_count, 1)
        self.assertEqual(get_raw_access_token.return_value.json.call_count, 1)

        # Test that a stripe account has been successfully
        # created for the explorer
        stripe_account = StripeAccount.objects.get(
            account_id=access_token_data.get('stripe_user_id'))
        check_attrs = [
            'stripe_publishable_key',
            'access_token',
            'livemode',
            'token_type',
            'scope',
            'refresh_token',
        ]
        for check_attr in check_attrs:
            self.assertEqual(
                getattr(stripe_account, check_attr),
                access_token_data.get(check_attr))

    @mock.patch('rauth.OAuth2Service.get_raw_access_token')
    def test_error_in_response_raises_permission_denied(self, get_raw_access_token):
        invalid_test_code = 'ac_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed)

        access_token_data = {
            'error_description': 'Authorization code does not exist: {0}'.format(invalid_test_code),
            'error': 'invalid_grant'
        }
        get_raw_access_token.return_value.json.return_value = access_token_data

        response = self.client.get(
            reverse('stripe_connect.response'),
            {'code': invalid_test_code})

        self.assertEqual(response.status_code, 403)
        
