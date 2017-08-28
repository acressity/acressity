from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from benefaction.models import Campaign, Bounty
from benefaction.tests.campaigns.test_main import CampaignTestCase
from experiences.models import Experience
from stripe_connect.models import StripeAccount, Charge


class CampaignMethodsTest(CampaignTestCase):
    def setUp(self):
        super(CampaignMethodsTest, self).setUp()

        StripeAccount.objects.create(
            explorer = self.explorer_author,
            account_id = 'acc_nonsense',
            customer_id = 'acc_nonsense',
            access_token = 'acc_nonsense',
            refresh_token = 'acc_nonsense',
            token_type = 'acc_nonsense',
            stripe_publishable_key = 'acc_nonsense',
            scope = 'acc_nonsense',
            livemode = False
        )

    def test_get_recipient_returns_experience_author(self):
        self.assertEqual(self.campaign.get_recipient(), self.campaign.experience.author)

    def test_get_level_returns_proper_value_for_bounties(self):
        bounty = Bounty.objects.create(
            campaign=self.campaign,
            creator=self.explorer_benefactor,
            proposition='I pick the color of the kayak',
            amount=100
        )
        bounty_child = Bounty.objects.create(
            campaign=self.campaign,
            parent=bounty,
            creator=self.explorer_author,
            proposition=bounty.proposition,
            amount=bounty.amount + 10
        )
        bounty_grandchild = Bounty.objects.create(
            campaign=self.campaign,
            parent=bounty_child,
            creator=self.explorer_benefactor,
            proposition=bounty_child.proposition,
            amount=bounty_child.amount - 5
        )

        self.assertEqual(bounty.get_level(), 0)
        self.assertEqual(bounty_child.get_level(), 1)
        self.assertEqual(bounty_grandchild.get_level(), 2)

    def test_get_first_level_returns_proper_bounties(self):
        bounty = Bounty.objects.create(
            campaign=self.campaign,
            creator=self.explorer_benefactor,
            proposition='Write me a poem',
            amount=50
        )
        child = Bounty.objects.create(
            campaign=self.campaign,
            parent=bounty,
            creator=self.explorer_author,
            proposition=bounty.proposition,
            amount=bounty.amount + 10
        )

        self.assertIn(bounty, self.campaign.get_first_level())
        self.assertNotIn(child, self.campaign.get_first_level())

    def test_get_amount_raised_returns_0_no_paid_bounties(self):
        self.assertEqual(self.campaign.get_amount_raised(), 0)

    def test_get_amount_raised_returns_proper_value_with_paid_bounties(self):
        bounty1 = Bounty.objects.create(
            campaign=self.campaign,
            creator=self.explorer_benefactor,
            proposition='Bring my son\'s action figure',
            description='Take at least 10 pictures with him in various poses/locations',
            amount=100
        )
        bounty2 = Bounty.objects.create(
            campaign=self.campaign,
            creator=self.explorer_benefactor,
            proposition='Just a donation',
            description='I always wanted to do this myself, too old now. I see myself in you.',
            amount=250
        )

        charge1 = Charge.objects.create(
            charge_id='ch_nonsense1',
            stripe_account=bounty1.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(bounty1),
            object_pk=bounty1.pk,
            amount_in_cents=bounty1.amount * 100,
            benefactor=self.explorer_benefactor
        )
        charge2 = Charge.objects.create(
            charge_id='ch_nonsense2',
            stripe_account=bounty2.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(bounty1),
            object_pk=bounty2.pk,
            amount_in_cents=bounty2.amount * 100,
            benefactor=self.explorer_benefactor
        )

        bounty1.save()
        bounty2.save()
        
        self.assertEqual(self.campaign.get_amount_raised(), bounty1.amount + bounty2.amount)

    def test_get_amount_raised_returns_proper_amount(self):
        self.assertEqual(self.campaign.get_amount_raised(), 0)

        # Create a payment for half the campaign funds
        bounty1 = Bounty.objects.create(
            campaign=self.campaign,
            creator=self.explorer_benefactor,
            proposition='Donation',
            description='No specifications',
            amount=101.50
        )

        charge = Charge.objects.create(
            charge_id='ch_nonsense1',
            stripe_account=bounty1.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(bounty1),
            object_pk=bounty1.pk,
            amount_in_cents=bounty1.amount * 100,
            benefactor=self.explorer_benefactor
        )
        
        self.assertEqual(self.campaign.get_amount_raised(), bounty1.amount)

        # Create payment for the rest of the funds
        bounty2 = Bounty.objects.create(
            campaign=self.campaign,
            creator=self.explorer_benefactor,
            proposition='Donation',
            description='No specifications',
            amount=98.71
        )

        charge = Charge.objects.create(
            charge_id='ch_nonsense2',
            stripe_account=bounty2.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(bounty2),
            object_pk=bounty2.pk,
            amount_in_cents=bounty2.amount * 100,
            benefactor=self.explorer_benefactor
        )

        self.assertEqual(float(self.campaign.get_amount_raised()), round(bounty1.amount + bounty2.amount, 2))

    def test_get_percent_raised_returns_proper_amount(self):
        self.assertEqual(self.campaign.get_percent_raised(), 0)

        # Create a payment for half the campaign funds
        bounty_half_funds1 = Bounty.objects.create(
            campaign=self.campaign,
            creator=self.explorer_benefactor,
            proposition='Donation to fulfill half of your request',
            description='No specifications!',
            amount=self.campaign.amount_requested / 2
        )

        charge = Charge.objects.create(
            charge_id='ch_nonsense1',
            stripe_account=bounty_half_funds1.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(bounty_half_funds1),
            object_pk=bounty_half_funds1.pk,
            amount_in_cents=bounty_half_funds1.amount * 100,
            benefactor=self.explorer_benefactor
        )
        
        self.assertEqual(self.campaign.get_percent_raised(), 50)

        # Create payment for the rest of the funds
        bounty_half_funds2 = Bounty.objects.create(
            campaign=self.campaign,
            creator=self.explorer_benefactor,
            proposition='Donation to fulfill rest of requested amount',
            description='No specifications!',
            amount=self.campaign.amount_requested / 2
        )

        charge = Charge.objects.create(
            charge_id='ch_nonsense2',
            stripe_account=bounty_half_funds2.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(bounty_half_funds2),
            object_pk=bounty_half_funds2.pk,
            amount_in_cents=bounty_half_funds2.amount * 100,
            benefactor=self.explorer_benefactor
        )

        self.assertEqual(self.campaign.get_percent_raised(), 100)

    def test_get_percent_raised_returns_max_100(self):
        # Create payment for 101% of funds
        bounty_101_percent = Bounty.objects.create(
            campaign=self.campaign,
            creator=self.explorer_benefactor,
            proposition='Paying 101% of requested amount',
            description='No specifications!',
            amount=self.campaign.amount_requested * 1.01
        )

        charge = Charge.objects.create(
            charge_id='ch_nonsense',
            stripe_account=bounty_101_percent.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(bounty_101_percent),
            object_pk=bounty_101_percent.pk,
            amount_in_cents=bounty_101_percent.amount * 100,
            benefactor=self.explorer_benefactor
        )

        self.assertEqual(self.campaign.get_percent_raised(), 100)

    def test_is_complete_returns_proper_value(self):
        self.assertFalse(self.campaign.is_complete())

        # Create a payment for half the campaign funds
        bounty_half_funds1 = Bounty.objects.create(
            campaign=self.campaign,
            creator=self.explorer_benefactor,
            proposition='Donation to fulfill half of your request',
            description='No specifications!',
            amount=self.campaign.amount_requested / 2
        )

        charge = Charge.objects.create(
            charge_id='ch_nonsense1',
            stripe_account=bounty_half_funds1.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(bounty_half_funds1),
            object_pk=bounty_half_funds1.pk,
            amount_in_cents=bounty_half_funds1.amount * 100,
            benefactor=self.explorer_benefactor
        )
        
        self.assertFalse(self.campaign.is_complete())

        # Create payment for the rest of the funds
        bounty_half_funds2 = Bounty.objects.create(
            campaign=self.campaign,
            creator=self.explorer_benefactor,
            proposition='Donation to fulfill rest of requested amount',
            description='No specifications!',
            amount=self.campaign.amount_requested / 2
        )

        charge = Charge.objects.create(
            charge_id='ch_nonsense2',
            stripe_account=bounty_half_funds2.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(bounty_half_funds2),
            object_pk=bounty_half_funds2.pk,
            amount_in_cents=bounty_half_funds2.amount * 100,
            benefactor=self.explorer_benefactor
        )

        self.assertTrue(self.campaign.is_complete())

    def test_is_complete_true_when_over_100_percent(self):
        # Create payment for 101% of funds
        bounty_101_percent = Bounty.objects.create(
            campaign=self.campaign,
            creator=self.explorer_benefactor,
            proposition='Paying 101% of requested amount',
            description='No specifications!',
            amount=self.campaign.amount_requested * 1.01
        )

        charge = Charge.objects.create(
            charge_id='ch_nonsense',
            stripe_account=bounty_101_percent.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(bounty_101_percent),
            object_pk=bounty_101_percent.pk,
            amount_in_cents=bounty_101_percent.amount * 100,
            benefactor=self.explorer_benefactor
        )

        self.assertTrue(self.campaign.is_complete())

