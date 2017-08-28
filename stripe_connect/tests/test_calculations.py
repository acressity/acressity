import stripe 

from django.test import TestCase, RequestFactory, TransactionTestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from stripe_connect.models import StripeAccount, Charge
from stripe_connect.tests.test_main import StripeTestCase
from benefaction.models import Campaign
from experiences.models import Experience
from explorers.models import Explorer
from explorers.tests import helpers as explorer_helpers

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeTestCalculations(StripeTestCase):
    def setUp(self):
        super(StripeTestCalculations, self).setUp()
        self.fee_percent = settings.ACRESSITY_SERVICE_PERCENTAGE
        self.explorer = explorer_helpers.create_test_explorer()

        self.campaign_experience = Experience.objects.create(
            title='Kayak the Colorado River',
            author=self.explorer,
            is_public=True
        )

        self.campaign = Campaign.objects.create(
            experience=self.campaign_experience,
            amount_requested=4000
        )

        stripe_account = StripeAccount.objects.create(
            explorer=self.explorer
        )

    def test_convert_amount_to_cents_correct_result(self):
        self.assertEqual(StripeAccount.to_cents(9.99), 999)
        self.assertEqual(StripeAccount.to_cents(9), 900)
        self.assertEqual(StripeAccount.to_cents(9.9), 990)

    def test_convert_amount_to_cents_returns_integer(self):
        self.assertIs(type(StripeAccount.to_cents(9.99)), int)
        self.assertIs(type(StripeAccount.to_cents(9)), int)
        self.assertIs(type(StripeAccount.to_cents(9.9)), int)

    def test_calculate_application_fee_correct_result(self):
        self.assertEqual(StripeAccount.calc_app_fee_cents(500.00), int(50000 * (self.fee_percent / 100.0)))
        self.assertEqual(StripeAccount.calc_app_fee_cents(501), int(50100 * (self.fee_percent / 100.0)))
        self.assertEqual(StripeAccount.calc_app_fee_cents(502.5), int(50250 * (self.fee_percent / 100.0)))

    def test_calculate_application_fee_returns_integer(self):
        self.assertIs(type(StripeAccount.calc_app_fee_cents(500.00)), int)
        self.assertIs(type(StripeAccount.calc_app_fee_cents(501)), int)
        self.assertIs(type(StripeAccount.calc_app_fee_cents(502.5)), int)
