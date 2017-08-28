from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from benefaction.models import Campaign, Bounty
from benefaction.tests.bounties.test_main import BountyTestCase
from experiences.models import Experience
from stripe_connect.models import StripeAccount, Charge


class BountyMethodsTest(BountyTestCase):
    def setUp(self):
        super(BountyMethodsTest, self).setUp()

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
        self.assertEqual(
            self.bounty_by_author.get_recipient(),
            self.bounty_by_author.campaign.experience.author
        )

    def test_get_children_returns_all_first_level_children(self):
        child1 = Bounty.objects.create(
            campaign=self.campaign,
            parent=self.bounty_by_benefactor,
            creator=self.explorer_author,
            proposition=self.bounty_by_benefactor.proposition,
            amount=self.bounty_by_benefactor.amount + 10
        )
        child2 = Bounty.objects.create(
            campaign=self.campaign,
            parent=self.bounty_by_benefactor,
            creator=self.explorer_other,
            proposition=self.bounty_by_benefactor.proposition,
            amount=self.bounty_by_benefactor.amount - 10
        )

        self.assertIn(child1, self.bounty_by_benefactor.get_children())
        self.assertIn(child2, self.bounty_by_benefactor.get_children())

    def test_get_children_returns_only_first_level_of_children(self):
        child = Bounty.objects.create(
            campaign=self.campaign,
            parent=self.bounty_by_benefactor,
            creator=self.explorer_author,
            proposition=self.bounty_by_benefactor.proposition,
            amount=self.bounty_by_benefactor.amount + 10
        )
        grandchild = Bounty.objects.create(
            campaign=self.campaign,
            parent=child,
            creator=self.explorer_benefactor,
            proposition=child.proposition,
            amount=child.amount - 5
        )

        self.assertIn(child, self.bounty_by_benefactor.get_children())
        self.assertNotIn(grandchild, self.bounty_by_benefactor.get_children())

    def test_get_children_returns_no_children_if_no_children(self):
        self.assertFalse(self.bounty_by_benefactor.get_children())

    def test_has_children_returns_true_when_has_child(self):
        child = Bounty.objects.create(
            campaign=self.campaign,
            parent=self.bounty_by_benefactor,
            creator=self.explorer_author,
            proposition=self.bounty_by_benefactor.proposition,
            amount=self.bounty_by_benefactor.amount + 10
        )

        self.assertTrue(self.bounty_by_benefactor.has_children())

    def test_has_children_returns_false_when_no_children(self):
        self.assertFalse(self.bounty_by_benefactor.has_children())

    def test_get_level_returns_proper_value_for_bounties(self):
        child = Bounty.objects.create(
            campaign=self.campaign,
            parent=self.bounty_by_benefactor,
            creator=self.explorer_author,
            proposition=self.bounty_by_benefactor.proposition,
            amount=self.bounty_by_benefactor.amount + 10
        )
        grandchild = Bounty.objects.create(
            campaign=self.campaign,
            parent=child,
            creator=self.explorer_benefactor,
            proposition=child.proposition,
            amount=child.amount - 5
        )

        self.assertEqual(self.bounty_by_benefactor.get_level(), 0)
        self.assertEqual(child.get_level(), 1)
        self.assertEqual(grandchild.get_level(), 2)

    def test_get_first_level_returns_proper_bounties(self):
        child = Bounty.objects.create(
            campaign=self.campaign,
            parent=self.bounty_by_benefactor,
            creator=self.explorer_benefactor,
            proposition=self.bounty_by_benefactor.proposition,
            amount=self.bounty_by_benefactor.amount - 5
        )

        self.assertIn(self.bounty_by_benefactor, self.campaign.get_first_level())
        self.assertIn(self.bounty_by_author, self.campaign.get_first_level())
        self.assertNotIn(child, self.campaign.get_first_level())

    def test_bounty_with_child_not_deletable(self):
        child = Bounty.objects.create(
            campaign=self.campaign,
            parent=self.bounty_by_benefactor,
            creator=self.explorer_author,
            proposition=self.bounty_by_benefactor.proposition,
            amount=self.bounty_by_benefactor.amount + 10
        )

        self.assertFalse(self.bounty_by_benefactor.deletable())

    def test_paid_bounty_not_deletable(self):
        charge = Charge.objects.create(
            charge_id='ch_nonsense1',
            stripe_account=self.bounty_by_benefactor.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(self.bounty_by_benefactor),
            object_pk=self.bounty_by_benefactor.pk,
            amount_in_cents=self.bounty_by_benefactor.amount * 100,
            benefactor=self.explorer_benefactor
        )

        self.assertFalse(self.bounty_by_benefactor.deletable())

    def test_bounty_with_child_not_editable(self):
        child = Bounty.objects.create(
            campaign=self.campaign,
            parent=self.bounty_by_benefactor,
            creator=self.explorer_author,
            proposition=self.bounty_by_benefactor.proposition,
            amount=self.bounty_by_benefactor.amount + 10
        )

        self.assertFalse(self.bounty_by_benefactor.editable())

    def test_paid_bounty_not_editable(self):
        charge = Charge.objects.create(
            charge_id='ch_nonsense1',
            stripe_account=self.bounty_by_benefactor.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(self.bounty_by_benefactor),
            object_pk=self.bounty_by_benefactor.pk,
            amount_in_cents=self.bounty_by_benefactor.amount * 100,
            benefactor=self.explorer_benefactor
        )

        self.assertFalse(self.bounty_by_benefactor.editable())

    def test_charges_returns_all_charges(self):
        charge1 = Charge.objects.create(
            charge_id='ch_nonsense1',
            stripe_account=self.bounty_by_benefactor.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(self.bounty_by_benefactor),
            object_pk=self.bounty_by_benefactor.pk,
            amount_in_cents=self.bounty_by_benefactor.amount * 100,
            benefactor=self.explorer_benefactor,
            is_refunded=True
        )

        self.assertEqual(list(self.bounty_by_benefactor.charges()), [charge1])

        charge2 = Charge.objects.create(
            charge_id='ch_nonsense2',
            stripe_account=self.bounty_by_benefactor.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(self.bounty_by_benefactor),
            object_pk=self.bounty_by_benefactor.pk,
            amount_in_cents=self.bounty_by_benefactor.amount * 100,
            benefactor=self.explorer_benefactor
        )

        self.assertEqual(list(self.bounty_by_benefactor.charges()), [charge1, charge2])

    def test_get_charge_returns_current_charge(self):
        charge1 = Charge.objects.create(
            charge_id='ch_nonsense1',
            stripe_account=self.bounty_by_benefactor.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(self.bounty_by_benefactor),
            object_pk=self.bounty_by_benefactor.pk,
            amount_in_cents=self.bounty_by_benefactor.amount * 100,
            benefactor=self.explorer_benefactor
        )

        self.assertEqual(self.bounty_by_benefactor.get_charge(), charge1)

        charge2 = Charge.objects.create(
            charge_id='ch_nonsense2',
            stripe_account=self.bounty_by_benefactor.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(self.bounty_by_benefactor),
            object_pk=self.bounty_by_benefactor.pk,
            amount_in_cents=self.bounty_by_benefactor.amount * 100,
            benefactor=self.explorer_benefactor
        )

        self.assertEqual(self.bounty_by_benefactor.get_charge(), charge2)

    def test_get_charge_returns_current_charge_even_if_refunded(self):
        charge1 = Charge.objects.create(
            charge_id='ch_nonsense1',
            stripe_account=self.bounty_by_benefactor.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(self.bounty_by_benefactor),
            object_pk=self.bounty_by_benefactor.pk,
            amount_in_cents=self.bounty_by_benefactor.amount * 100,
            benefactor=self.explorer_benefactor
        )

        self.assertEqual(self.bounty_by_benefactor.get_charge(), charge1)

        charge2 = Charge.objects.create(
            charge_id='ch_nonsense2',
            stripe_account=self.bounty_by_benefactor.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(self.bounty_by_benefactor),
            object_pk=self.bounty_by_benefactor.pk,
            amount_in_cents=self.bounty_by_benefactor.amount * 100,
            benefactor=self.explorer_benefactor,
            is_refunded=True
        )

        self.assertEqual(self.bounty_by_benefactor.get_charge(), charge2)

    def test_get_charge_returns_current_charge_even_if_refunded(self):
        charge1 = Charge.objects.create(
            charge_id='ch_nonsense1',
            stripe_account=self.bounty_by_benefactor.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(self.bounty_by_benefactor),
            object_pk=self.bounty_by_benefactor.pk,
            amount_in_cents=self.bounty_by_benefactor.amount * 100,
            benefactor=self.explorer_benefactor,
            is_refunded=True
        )

        self.assertEqual(self.bounty_by_benefactor.get_charge(), charge1)

    def test_is_paid_false_when_no_charges(self):
        self.assertEqual(list(self.bounty_by_benefactor.charges()), [])
        self.assertFalse(self.bounty_by_benefactor.is_paid())

    def test_is_paid_when_has_charge_not_refunded(self):
        charge1 = Charge.objects.create(
            charge_id='ch_nonsense1',
            stripe_account=self.bounty_by_benefactor.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(self.bounty_by_benefactor),
            object_pk=self.bounty_by_benefactor.pk,
            amount_in_cents=self.bounty_by_benefactor.amount * 100,
            benefactor=self.explorer_benefactor,
        )

        self.assertTrue(self.bounty_by_benefactor.is_paid())

    def test_is_paid_false_when_has_charge_refunded(self):
        charge1 = Charge.objects.create(
            charge_id='ch_nonsense1',
            stripe_account=self.bounty_by_benefactor.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(self.bounty_by_benefactor),
            object_pk=self.bounty_by_benefactor.pk,
            amount_in_cents=self.bounty_by_benefactor.amount * 100,
            benefactor=self.explorer_benefactor,
            is_refunded=True
        )

        self.assertFalse(self.bounty_by_benefactor.is_paid())

    def test_is_paid_false_when_has_charge_less_than_amount(self):
        charge1 = Charge.objects.create(
            charge_id='ch_nonsense1',
            stripe_account=self.bounty_by_benefactor.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(self.bounty_by_benefactor),
            object_pk=self.bounty_by_benefactor.pk,
            amount_in_cents=(self.bounty_by_benefactor.amount * 100) - 0.01,
            benefactor=self.explorer_benefactor,
        )

        self.assertFalse(self.bounty_by_benefactor.is_paid())
