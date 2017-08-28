from datetime import date

from django import forms
from narratives.models import Narrative
from django.forms.extras.widgets import SelectDateWidget
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

TRANSFER_ACTION_CHOICES = (
    ('', '-----'),
    (1, _('Transfer')),
    (2, _('Copy')),
)


class NarrativeForm(forms.ModelForm):
    class Meta:
        model = Narrative
        fields = (
            'title',
            'body',
            'experience',
            'date_created',
            'category',
            'is_public',
        )
        widgets = {
            'date_created': SelectDateWidget(years=range(timezone.now().year, timezone.now().year - 110, -1)),
            'title': forms.TextInput(
                attrs={
                    'onfocus': 'if($(this).val()==this.defaultValue){$(this).val("")};',
                    'onblur': 'if($(this).val()==""){$(this).val(this.defaultValue)};',
                }),
        }
        labels = {
            'body': _('Narrative'),
            'is_public': _('Public?'),
        }
        help_texts = {
            'date_created': _('Leave blank for today'),
        }

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author', None)
        super(NarrativeForm, self).__init__(*args, **kwargs)
        self.fields['experience'].queryset = self.author.experiences.all()

    def save(self, commit=True):
        instance = super(NarrativeForm, self).save(commit=False)
        if self.author:
            instance.author = self.author
        if commit:
            instance.save()
        return instance

    def clean_date_created(self):
        date_created = self.cleaned_data.get('date_created')
        if not date_created:
            date_created = timezone.now()
        return date_created

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if len(body) < 3:
            raise forms.ValidationError('The narrative body needs a little more extrapolation')
        return body


class NarrativeTransferForm(forms.ModelForm):
    potential_actions = forms.ChoiceField(choices=TRANSFER_ACTION_CHOICES, required=False)

    class Meta:
        model = Narrative
        fields = ('title',)
