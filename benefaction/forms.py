from datetime import datetime

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.forms import ModelForm
from django.shortcuts import get_object_or_404

from benefaction.models import Campaign, Bounty


class CampaignForm(ModelForm):
    class Meta:
        model = Campaign
        exclude = ()


class BountyForm(ModelForm):
    class Meta:
        model = Bounty
        fields = [
            'parent',
            'proposition',
            'amount',
            'description',
        ]
        widgets = {
            'parent': forms.HiddenInput(),
        }

