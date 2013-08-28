from datetime import datetime

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.forms import ModelForm
from django.shortcuts import get_object_or_404

from support.models import InvitedExplorer


class InvitedExplorerForm(ModelForm):

    class Meta:
        model = InvitedExplorer
        exclude = ('code',)

    def __init__(self, explorer, *args, **kwargs):
        super(InvitedExplorerForm, self).__init__(*args, **kwargs)
        self.fields['experience'].queryset = explorer.experiences.all()

    def clean_experience(self):
        experience = self.cleaned_data.get('experience')
        if not experience:
            raise forms.ValidationError('You must select an experience to invite this person to')
        return experience
