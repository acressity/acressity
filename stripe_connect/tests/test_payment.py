import stripe 
import mock

from django.test import TestCase, RequestFactory, TransactionTestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
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
class StripeTestPayment(StripeTestCase):
    valid_token_id = MockToken.token_data[0].get('id')
    invalid_token_id = 'tok_XXXXXXXXXXXXXXXXXXXXXXXX'

    def test_benefactor_payment_sets_bounty_paid_status(self):
        data = {
            'stripeToken': self.valid_token_id,
        }

        self.client.login(
            username=self.explorer_benefactor_authorized.email,
            password=self.explorer_benefactor_authorized.password_unhashed
        )

        self.assertFalse(self.bounty_by_author.is_paid())

        response = self.client.post(
            reverse('stripe_connect.bounty.payment', 
                args=(self.bounty_by_author.pk,)
            ),
            data
        )

        self.assertTrue(self.bounty_by_author.is_paid())

    def test_benefactor_payment_changes_amount_raised(self):
        initial_amount_raised = self.campaign.get_amount_raised()
        data = {
            'stripeToken': self.valid_token_id,
        }

        self.client.login(
            username=self.explorer_benefactor_authorized.email,
            password=self.explorer_benefactor_authorized.password_unhashed
        )

        response = self.client.post(
            reverse('stripe_connect.bounty.payment', 
                args=(self.bounty_by_author.pk,)
            ),
            data
        )

        self.assertEqual(self.campaign.get_amount_raised(), self.bounty_by_author.amount + initial_amount_raised) 

    def test_benefactor_payment_sets_benefactor(self):
        data = {
            'stripeToken': self.valid_token_id,
        }

        self.client.login(
            username=self.explorer_benefactor_authorized.email,
            password=self.explorer_benefactor_authorized.password_unhashed
        )

        response = self.client.post(
            reverse('stripe_connect.bounty.payment', 
                args=(self.bounty_by_author.pk,)
            ),
            data
        )

        self.assertEqual(self.bounty_by_author.get_benefactor(), self.explorer_benefactor_authorized) 

    def test_benefactor_new_payment_method_is_saved(self):
        data = {
            'stripeToken': self.valid_token_id,
        }

        self.client.login(
            username=self.explorer_benefactor_authorized.email,
            password=self.explorer_benefactor_authorized.password_unhashed
        )

        response = self.client.post(
            reverse('stripe_connect.bounty.payment', 
                args=(self.bounty_by_author.pk,)
            ),
            data
        )

        self.assertEqual(self.bounty_by_author.get_benefactor(), self.explorer_benefactor_authorized) 

    def test_anonymous_user_payment_sets_paid_status(self):
        data = {
            'stripeToken': self.valid_token_id,
        }

        self.assertFalse(self.bounty_by_author.is_paid())

        response = self.client.post(
            reverse('stripe_connect.bounty.payment', 
                args=(self.bounty_by_author.pk,)
            ),
            data
        )

        self.assertTrue(self.bounty_by_author.is_paid())

    def test_anonymous_user_payment_does_not_set_benefactor(self):
        data = {
            'stripeToken': self.valid_token_id,
        }

        self.assertFalse(self.bounty_by_author.is_paid())

        response = self.client.post(
            reverse('stripe_connect.bounty.payment', 
                args=(self.bounty_by_author.pk,)
            ),
            data
        )

        self.assertIsNone(self.bounty_by_author.get_benefactor())

    def test_anonymous_user_payment_updates_amount_raised(self):
        initial_amount_raised = self.campaign.get_amount_raised()
        data = {
            'stripeToken': self.valid_token_id,
        }

        response = self.client.post(
            reverse('stripe_connect.bounty.payment', 
                args=(self.bounty_by_author.pk,)
            ),
            data
        )

        self.assertEqual(self.campaign.get_amount_raised(), initial_amount_raised + self.bounty_by_author.amount)

    def test_payment_with_invalid_token_raises_invalid_error(self):
        initial_amount_raised = self.campaign.get_amount_raised()

        data = {
            'stripeToken': self.invalid_token_id,
        }

        self.client.login(
            username=self.explorer_benefactor_authorized.email,
            password=self.explorer_benefactor_authorized.password_unhashed
        )

        with self.assertRaises(InvalidRequestError):
            response = self.client.post(
                reverse('stripe_connect.bounty.payment', 
                    args=(self.bounty_by_author.pk,)
                ),
                data
            )

    @mock.patch('benefaction.models.Campaign.is_complete')
    def test_payment_to_raised_campaign_does_not_update_amount_raised(self, is_complete_mock):
        is_complete_mock.return_value = True
        initial_amount_raised = self.campaign.get_amount_raised()
        data = {
            'stripeToken': self.valid_token_id,
        }

        self.client.login(
            username=self.explorer_benefactor_authorized.email,
            password=self.explorer_benefactor_authorized.password_unhashed
        )

        response = self.client.post(
            reverse('stripe_connect.bounty.payment', 
                args=(self.bounty_by_author.pk,)
            ),
            data
        )

        self.assertEqual(self.campaign.get_amount_raised(), initial_amount_raised)

    @mock.patch('benefaction.models.Campaign.is_complete')
    def test_payment_to_raised_campaign_does_not_set_is_paid(self, is_complete_mock):
        is_complete_mock.return_value = True
        data = {
            'stripeToken': self.valid_token_id,
        }

        self.client.login(
            username=self.explorer_benefactor_authorized.email,
            password=self.explorer_benefactor_authorized.password_unhashed
        )

        response = self.client.post(
            reverse('stripe_connect.bounty.payment', 
                args=(self.bounty_by_author.pk,)
            ),
            data
        )

        self.assertFalse(self.bounty_by_author.is_paid())

