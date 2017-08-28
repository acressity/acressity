from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import View, DetailView, TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from experiences.models import Experience
from notifications import notify
from benefaction.forms import CampaignForm, BountyForm
from benefaction.models import Campaign, Bounty


class CampaignIndex(DetailView):
    model = Campaign
    template_name = 'benefaction/campaigns/index.html'
    contect_object_name = 'campaign'

    def dispatch(self, request, *args, **kwargs):
        if not self.get_object().can_access(
            request.user,
            request.get_signed_cookie('experience_password', salt='personal_domain', default=False)):
            if self.get_experience().password:
                return redirect(reverse('experience_check_password', args=[self.get_experience().id]))
            else:
                raise PermissionDenied
        return super(CampaignIndex, self).dispatch(request, *args, **kwargs)

    def get_experience(self):
        return self.model.objects.get(pk=self.kwargs.get('pk')).experience


class CampaignCreate(CreateView):
    model = Campaign
    template_name = 'benefaction/campaigns/create.html'
    fields = ['amount_requested', 'brief']

    def dispatch(self, request, *args, **kwargs):
        if request.user != self.get_experience().author:
            raise PermissionDenied
        if self.get_experience().has_campaign():
            messages.error(request, 'This experience already has a benefaction campaign')
            return redirect(self.get_experience().campaign)

        return super(CreateView, self).dispatch(request, *args, **kwargs)

    def get_experience(self):
        return get_object_or_404(
            Experience,
            pk=self.kwargs['experience_pk']
        )

    def form_valid(self, form):
        experience = self.get_experience()

        if self.request.user != experience.author:
            raise PermissionDenied
        form.instance.experience = experience
        return super(CampaignCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CampaignCreate, self).get_context_data(**kwargs)
        context['acressity_fee'] = settings.ACRESSITY_SERVICE_PERCENTAGE
        context['stripe_fee'] = settings.STRIPE_SERVICE_PERCENTAGE
        return context

    def get_success_url(self):
        return self.object.get_absolute_url()

class CampaignEdit(UpdateView):
    model = Campaign
    template_name = 'benefaction/campaigns/edit.html'
    fields = ['amount_requested', 'brief']

    def get_object(self, queryset=None):
        campaign = super(CampaignEdit, self).get_object()
        if not self.request.user == campaign.get_recipient():
            raise PermissionDenied
        return campaign

    def get_success_url(self):
        return self.object.get_absolute_url()


class CampaignDelete(DeleteView):
    model = Campaign
    template_name = 'benefaction/campaigns/delete.html'
    context_object_name = 'campaign'

    def get_object(self, queryset=None):
        campaign = super(CampaignDelete, self).get_object()
        if not self.request.user == campaign.get_recipient():
            raise PermissionDenied
        return campaign

    def get_success_url(self):
        return reverse(
            'experience',
            args=[self.object.experience.pk]
        )


class CampaignPaidBountiesListView(ListView):
    context_object_name = 'bounties'
    template_name = 'benefaction/campaigns/paid_bounties.html'
    
    def get_campaign(self):
        return get_object_or_404(Campaign, pk=self.kwargs.get('pk'))

    def get_queryset(self):
        self.campaign = get_object_or_404(Campaign, pk=self.kwargs.get('pk'))
        return [bounty for bounty in self.campaign.bounties.all() if bounty.is_paid()]

    def get_context_data(self, **kwargs):
        context = super(CampaignPaidBountiesListView, self).get_context_data(**kwargs)
        context['campaign'] = get_object_or_404(Campaign, pk=self.kwargs.get('pk'))
        return context


class CampaignFulfilledBountiesListView(ListView):
    context_object_name = 'bounties'
    template_name = 'benefaction/campaigns/fulfilled_bounties.html'
    
    def get_campaign(self):
        return get_object_or_404(Campaign, pk=self.kwargs.get('pk'))

    def get_queryset(self):
        self.campaign = self.get_campaign()
        return self.campaign.bounties.filter(is_fulfilled=True)

    def get_context_data(self, **kwargs):
        context = super(CampaignFulfilledBountiesListView, self).get_context_data(**kwargs)
        context['campaign'] = self.campaign
        return context


class BountyIndex(DetailView):
    model = Bounty
    template_name = 'benefaction/bounties/index.html'
    contect_object_name = 'bounty'

    def dispatch(self, request, *args, **kwargs):
        if not self.get_object().can_access(
            request.user,
            request.get_signed_cookie('experience_password', salt='personal_domain', default=False)):
            if self.get_experience().password:
                return redirect(reverse('experience_check_password', args=[self.get_experience().id]))
            else:
                raise PermissionDenied
        return super(BountyIndex, self).dispatch(request, *args, **kwargs)

    def get_experience(self):
        return self.model.objects.get(pk=self.kwargs.get('pk')).campaign.experience


class BountyCreate(CreateView):
    form_class = BountyForm
    template_name = 'benefaction/bounties/create.html'

    def form_valid(self, form):
        campaign = get_object_or_404(
            Campaign,
            pk=self.kwargs['campaign_pk']
        )
        form.instance.campaign = campaign
        form.instance.creator = self.request.user

        if self.request.user == campaign.get_recipient():
            form.instance.is_accepted = True

        # Save object so it can be used for notifications
        self.object = form.save()

        if form.instance.parent:
            notify.send(
                sender=self.request.user,
                recipient=form.instance.parent.creator,
                target=self.object,
                verb='''
                    has created a counter to bounty {0}. You can choose to accept or counter with a new bounty.
                '''.format(self.object)
            )
        elif self.request.user != campaign.get_recipient():
            notify.send(
                sender=self.request.user,
                recipient=campaign.get_recipient(),
                target=self.object,
                verb='''
                    has created a new bounty for {0}. You can choose to accept or counter with a new bounty.
                '''.format(self.object.campaign)
            )
        return super(BountyCreate, self).form_valid(form)

    def get_initial(self):
        if self.kwargs.get('bounty_pk'):
            # This is a bounty counterbid. Load the countered bounty info
            bounty_countered = get_object_or_404(
                Bounty,
                pk=self.kwargs.get('bounty_pk')
            )
            return {
                'parent': bounty_countered,
                'proposition': bounty_countered.proposition,
                'amount': bounty_countered.amount,
                'description': bounty_countered.description,
            }

    def get_context_data(self, **kwargs):
        context = super(BountyCreate, self).get_context_data(**kwargs)
        context['campaign'] = Campaign.objects.get(pk=self.kwargs['campaign_pk'])
        if self.kwargs.get('bounty_pk'):
            context['parent'] = Bounty.objects.get(pk=self.kwargs['bounty_pk'])
        return context

    def get_success_url(self):
        return self.object.get_absolute_url()


class BountyEdit(UpdateView):
    model = Bounty
    form_class = BountyForm
    template_name = 'benefaction/bounties/edit.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.get_object().editable():
            messages.error(self.request, 'You cannot edit this bounty')
            return redirect(self.get_object())
        return super(BountyEdit, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        bounty = super(BountyEdit, self).get_object()
        if self.request.user != bounty.creator:
            raise PermissionDenied
        return bounty

    def get_success_url(self):
        return self.object.get_absolute_url()


class BountyDelete(DeleteView):
    model = Bounty
    template_name = 'benefaction/bounties/delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.object.deletable():
            messages.error(request, 'You cannot delete this bounty')
            return redirect(self.object)
        return super(BountyDelete, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        bounty = super(BountyDelete, self).get_object()
        if not self.request.user in [bounty.get_recipient(), bounty.creator]:
            raise PermissionDenied
        return bounty

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()

class BountyAccept(DetailView):
    model = Bounty
    template_name = 'benefaction/bounties/accept.html'
    context_object_name = 'bounty'
    field = 'is_accepted'
    value = True

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.request.user != self.object.get_recipient():
            raise PermissionDenied

        if self.request.user == self.object.creator:
            raise PermissionDenied

        if self.object.is_accepted:
            messages.error(self.request, 'You have already accepted that bid')
            return redirect(self.object)

        if self.object.is_paid():
            raise PermissionDenied

        return super(BountyAccept, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        setattr(self.object, self.field, self.value)
        self.object.save()
        notify.send(
            sender=self.request.user,
            recipient=self.get_object().creator,
            target=self.get_object(),
            verb='''
                has accepted your bounty {0}. Visit the bounty page where you can send them the payment.
            '''.format(self.get_object().proposition)
        )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return self.object.get_absolute_url()


class BountyCancelAccept(DetailView):
    model = Bounty
    template_name = 'benefaction/bounties/cancel_accept.html'
    context_object_name = 'bounty'
    field = 'is_accepted'
    value = False

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.request.user != self.object.get_recipient():
            raise PermissionDenied

        if self.object.creator == self.object.get_recipient():
            raise PermissionDenied

        if not self.object.is_accepted:
            messages.error(self.request, 'You hadn\'t yet accepted that bounty')
            return redirect(self.object)

        if self.object.is_paid():
            raise PermissionDenied

        return super(BountyCancelAccept, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        setattr(self.object, self.field, self.value)
        self.object.save()
        notify.send(
            sender=self.request.user,
            recipient=self.get_object().creator,
            target=self.get_object(),
            verb='''
                has cancelled their acceptance of your bounty {0}.
            '''.format(self.get_object().proposition)
        )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return self.object.get_absolute_url()

