import requests
import json
import stripe

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.views.generic import View, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType

from stripe_connect.models import StripeAccount, Charge
from stripe_connect.config import stripe_event_types
from benefaction.models import Bounty
from experiences.models import Experience
from explorers.models import Explorer
from notifications import notify

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeAuthorize(TemplateView):
    model = StripeAccount
    template_name = 'stripe_connect/authorize.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_stripe_connected():
            messages.error(request, 'You already have a Stripe account connected to your journey')
            raise PermissionDenied

        return super(StripeAuthorize, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StripeAuthorize, self).get_context_data(**kwargs)

        context['stripe_authorize_url_for_explorer'] = self.model.gen_auth_url_explorer(self.request.user)
        context['stripe'] = StripeAccount
        context['acressity_service_percentage'] = settings.ACRESSITY_SERVICE_PERCENTAGE

        return context


class StripeResponse(TemplateView):
    '''
    Receives response code from authorization request which is used to
    generate an access token.
    '''

    model = StripeAccount
    template_name = 'stripe_connect/response.html'

    def get_context_data(self, **kwargs):
        context = super(StripeResponse, self).get_context_data(**kwargs)
        context['stripe_dashboard_url'] = StripeAccount.stripe_dashboard_url
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_stripe_connected():
            messages.error(request, 'You already have a Stripe account authorized')
            raise PermissionDenied

        return super(StripeResponse, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        data = {
            'grant_type': 'authorization_code',
            'client_id': settings.STRIPE_CLIENT_ID,
            'client_secret': settings.STRIPE_SECRET_KEY,
            'code': code,
        }

        # Send back data to receive token
        response = self.model.connect_oauth_service().get_raw_access_token('POST', data=data)
        stripe_payload = response.json()

        if stripe_payload.get('error'):
            messages.error(request, 'Stripe authorization not successful')
            raise PermissionDenied

        account_defaults = {
            'account_id': stripe_payload.get('stripe_user_id'),
            'access_token': stripe_payload.get('access_token'),
            'refresh_token': stripe_payload.get('refresh_token'),
            'token_type': stripe_payload.get('token_type'),
            'stripe_publishable_key': stripe_payload.get('stripe_publishable_key'),
            'scope': stripe_payload.get('scope'),
            'livemode': stripe_payload.get('livemode'),
            'is_deauthorized': False,
        }

        stripe_account, account_created = StripeAccount.objects.update_or_create(
            explorer=request.user,
            defaults=account_defaults)

        if stripe_account.customer_id is None:
            # Creating account for the first time
            # Initialize a new empty customer for the explorer
            customer = stripe.Customer.create(
                description=request.user.email)
            stripe_account.customer_id = customer.get('id')
            stripe_account.save()

        return super(StripeResponse, self).get(request, *args, **kwargs)


class StripePayment(DetailView):
    model = Bounty
    template_name = 'stripe_connect/payment.html'
    context_object_name = 'bounty'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.object.get_recipient().has_stripe_account() or \
            not self.object.get_recipient().stripe_account.fetch_stripe_is_connected():
            messages.error(request, 'The experience author does not have Stripe configured')
            return HttpResponseRedirect(self.object.get_absolute_url())

        if self.object.is_paid():
            messages.error(request, 'A payment for this bounty has already been processed')
            return HttpResponseRedirect(self.object.get_absolute_url())

        if self.object.campaign.is_complete():
            messages.error(request, 'The funds for this campaign have already been successfully raised')
            return HttpResponseRedirect(self.object.get_absolute_url())

        if request.user == self.object.get_recipient():
            messages.error(request, 'You cannot make a payment to your own campaign')
            return HttpResponseRedirect(self.object.get_absolute_url())

        return super(StripePayment, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StripePayment, self).get_context_data(**kwargs)
        context['stripe_publishable_key'] = settings.STRIPE_PUBLIC_KEY
        return context

    def post(self, request, *args, **kwargs):
        try:
            if request.POST.get('stripeToken'):
                token = stripe.Token.retrieve(request.POST.get('stripeToken'))

                if request.user.is_authenticated() and request.user.has_stripe_account():
                    customer = request.user.stripe_account.fetch_customer()
                    fingerprint = token.get(token.get('type')).get('fingerprint')
                    source_fingerprints = [source.get('fingerprint') for source in customer.sources.get('data')]
                    # If customer doesn't already have this source, add to list
                    if fingerprint not in source_fingerprints:
                        customer.sources.create(
                            source=token)
                        # Need new token after last one used to
                        # create new source
                        token = stripe.Token.create(
                            customer=customer.get('id'),
                            stripe_account=self.object.get_recipient().stripe_account.account_id)
            else:
                # Customer chose to pay with default source
                token = stripe.Token.create(
                    customer=request.user.stripe_account.customer_id,
                    stripe_account=self.object.get_recipient().stripe_account.account_id)

            stripe_charge = stripe.Charge.create(
                amount=StripeAccount.to_cents(self.object.amount),
                currency='usd',
                source=token,
                description='Bounty to fulfill: {0}'.format(self.object.proposition),
                application_fee=StripeAccount.calc_app_fee_cents(self.object.amount),
                stripe_account=self.object.get_recipient().stripe_account.account_id)
        except stripe.error.CardError:
            messages.error(request, 'Your card was not accepted')
            return HttpResponseRedirect(self.object.bounty.get_absolute_url())

        if stripe_charge.get('paid'):
            charge = Charge.objects.create(
                charge_id=stripe_charge.get('id'),
                stripe_account=self.object.get_recipient().stripe_account,
                content_type=ContentType.objects.get_for_model(self.object),
                object_pk=self.object.pk,
                amount_in_cents=stripe_charge.get('amount'),
                benefactor=request.user if request.user.is_authenticated() else None)

            if not request.user.is_authenticated():
                sender = self.object.campaign
                verb = 'has received an anonymous payment. You are now responsible for fulfilling the proposition of the bounty.'
            else:
                sender = request.user
                verb = 'has paid a bounty! You are now responsible for fulfilling the proposition of the bounty.'

            notify.send(
                sender=sender,
                recipient=self.object.get_recipient(),
                target=self.object,
                verb=verb)
            messages.success(request, 'Your payment was successfully posted!')
        else:
            messages.error(request, 'Your payment was not successful')
        return HttpResponseRedirect(self.object.get_absolute_url())


@require_POST
@csrf_exempt
def stripe_webhook(request, *args, **kwargs):
    data = json.loads(request.body)
    event_type = data.get('type')
    if event_type not in stripe_event_types:
        return HttpResponse(403)
    elif event_type == 'charge.refunded':
        charge = Charge.objects.get(
            charge_id=data['data']['object']['id'])
        if data['data']['object']['amount_refunded'] == charge.amount_in_cents:
            charge.is_refunded = True
            charge.save()
    elif event_type == 'account.application.deauthorized':
        stripe_account = StripeAccount.objects.get(
            account_id=data['user_id'])
        stripe_account.is_deauthorized = True
        stripe_account.save()
    return HttpResponse(status=200)


class StripeDisconnect(DetailView):
    model = StripeAccount
    template_name = 'stripe_connect/disconnect.html'
    context_object_name = 'stripe_account'

    def get_success_url(self):
        return self.request.user.get_absolute_url()

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.request.user != self.object.explorer:
            raise PermissionDenied

        if not self.request.user.has_stripe_account():
            messages.error(self.request, 'You do not have a stripe account connected')
            return HttpResponseRedirect(self.request.user.get_absolute_url())

        if self.object != self.request.user.stripe_account:
            raise PermissionDenied
        
        return super(StripeDisconnect, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            self.object.disconnect_account()
            messages.success(request, 'You have been successfully disconnected')
            return HttpResponseRedirect(self.get_success_url())
        except:
            messages.error(request, 'You were not successfully disconnected')
        return HttpResponseRedirect(self.request.user.get_absolute_url())


class StripeAbout(TemplateView):
    template_name = 'stripe_connect/about.html'
    
    def get_context_data(self, **kwargs):
        context = super(StripeAbout, self).get_context_data(**kwargs)
        context['stripe'] = StripeAccount
        if self.request.user.is_authenticated():
            if not self.request.user.is_stripe_connected():
                context['stripe_authorize_url'] = StripeAccount.gen_auth_url_explorer(self.request.user)
        return context
