from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from benefaction.models import Campaign, Bounty
from benefaction.tests.bounties.test_main import BountyTestCase
from experiences.models import Experience
from stripe_connect.models import StripeAccount, Charge


class BountyDeleteTest(BountyTestCase):
    def setUp(self):
        super(BountyDeleteTest, self).setUp()

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

    def test_author_can_view_delete_own_bounty_page(self):
        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )
        response = self.client.get(reverse('bounty.delete',
                args=(self.bounty_by_author.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_author_can_view_delete_benefactor_bounty_page(self):
        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )
        response = self.client.get(reverse('bounty.delete',
                args=(self.bounty_by_benefactor.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_benefactor_can_view_delete_own_bounty_page(self):
        self.client.login(
            username=self.explorer_benefactor.email,
            password=self.explorer_benefactor.password_unhashed
        )
        response = self.client.get(reverse('bounty.delete',
                args=(self.bounty_by_benefactor.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_benefactor_cannot_view_delete_author_bounty_page(self):
        self.client.login(
            username=self.explorer_benefactor.email,
            password=self.explorer_benefactor.password_unhashed
        )
        response = self.client.get(reverse('bounty.delete',
                args=(self.bounty_by_author.pk,)))
        self.assertEqual(response.status_code, 403)

    def test_comrade_cannot_view_delete_author_bounty_page(self):
        self.bounty_by_author.campaign.experience.explorers.add(self.explorer_other)

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.get(reverse('bounty.delete',
                args=(self.bounty_by_author.pk,)))
        self.assertEqual(response.status_code, 403)

    def test_comrade_cannot_view_delete_benefactor_bounty_page(self):
        self.bounty_by_author.campaign.experience.explorers.add(self.explorer_other)

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.get(reverse('bounty.delete',
                args=(self.bounty_by_benefactor.pk,)))
        self.assertEqual(response.status_code, 403)

    def test_non_comrade_cannot_view_delete_bounty_page(self):
        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.get(reverse('bounty.delete',
                args=(self.bounty_by_author.pk,)))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_directed_login_to_view_delete_bounty(self):
        response = self.client.get(
            reverse('bounty.delete',
                args=(self.bounty_by_author.pk,))
        )
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' +
                reverse('bounty.delete', args=(self.bounty_by_author.pk,)))

    def test_author_can_delete_own_bounty(self):
        num_bounties_start = self.campaign.bounties.count()

        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )
        response = self.client.post(reverse('bounty.delete',
                args=(self.bounty_by_author.pk,)))

        self.assertEqual(
            self.campaign.bounties.count(),
            num_bounties_start - 1
        )

    def test_author_can_delete_benefactor_bounty(self):
        num_bounties_start = self.campaign.bounties.count()

        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )
        response = self.client.post(reverse('bounty.delete',
                args=(self.bounty_by_benefactor.pk,)))

        self.assertEqual(
            self.campaign.bounties.count(),
            num_bounties_start - 1
        )

    def test_author_cannot_delete_paid_bounty(self):
        num_bounties_start = self.campaign.bounties.count()

        charge = Charge.objects.create(
            charge_id='ch_nonsense1',
            stripe_account=self.bounty_by_author.get_recipient().stripe_account,
            content_type=ContentType.objects.get_for_model(self.bounty_by_author),
            object_pk=self.bounty_by_author.pk,
            amount_in_cents=self.bounty_by_author.amount * 100,
            benefactor=self.explorer_benefactor
        )

        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )
        response = self.client.post(reverse('bounty.delete',
                args=(self.bounty_by_author.pk,)))

        self.assertEqual(
            self.campaign.bounties.count(),
            num_bounties_start
        )
        self.assertEqual(response.status_code, 302)

    def test_author_cannot_delete_bounty_with_child(self):
        bounty_child = Bounty.objects.create(
            campaign=self.campaign,
            parent=self.bounty_by_author,
            creator=self.explorer_benefactor,
            amount=self.bounty_by_author.amount - 10,
            proposition=self.bounty_by_author.proposition + ' and do it blindfolded'
        )

        num_bounties_start = self.campaign.bounties.count()

        self.client.login(
            username=self.explorer_author.email,
            password=self.explorer_author.password_unhashed
        )
        response = self.client.post(reverse('bounty.delete',
                args=(self.bounty_by_author.pk,)))

        self.assertEqual(
            self.campaign.bounties.count(),
            num_bounties_start
        )
        self.assertEqual(response.status_code, 302)

    def test_benefactor_can_delete_own_bounty(self):
        num_bounties_start = self.campaign.bounties.count()

        self.client.login(
            username=self.explorer_benefactor.email,
            password=self.explorer_benefactor.password_unhashed
        )
        response = self.client.post(reverse('bounty.delete',
                args=(self.bounty_by_benefactor.pk,)))

        self.assertEqual(
            self.campaign.bounties.count(),
            num_bounties_start - 1
        )

    def test_comrade_cannot_delete_author_bounty(self):
        num_bounties_start = self.campaign.bounties.count()

        self.campaign.experience.explorers.add(self.explorer_other)

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.post(reverse('bounty.delete',
                args=(self.bounty_by_author.pk,)))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            self.campaign.bounties.count(),
            num_bounties_start
        )

    def test_comrade_cannot_delete_author_bounty(self):
        num_bounties_start = self.campaign.bounties.count()

        self.campaign.experience.explorers.add(self.explorer_other)

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )
        response = self.client.post(reverse('bounty.delete',
                args=(self.bounty_by_benefactor.pk,)))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            self.campaign.bounties.count(),
            num_bounties_start
        )

    def test_non_comrade_cannot_delete_author_bounty(self):
        num_bounties_start = self.campaign.bounties.count()

        self.client.login(
            username=self.explorer_other.email,
            password=self.explorer_other.password_unhashed
        )

        response = self.client.post(reverse('bounty.delete',
                args=(self.bounty_by_author.pk,)))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            self.campaign.bounties.count(),
            num_bounties_start
        )

    def test_anonymous_user_directed_login_to_delete_bounty(self):
        num_bounties_start = self.campaign.bounties.count()

        response = self.client.post(
            reverse('bounty.delete',
                args=(self.bounty_by_author.pk,))
        )
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' +
                reverse('bounty.delete', args=(self.bounty_by_author.pk,)))
