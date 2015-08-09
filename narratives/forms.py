from datetime import date

from django import forms
from django.forms import ModelForm
from narratives.models import Narrative
from django.forms.extras.widgets import SelectDateWidget
from django.utils import timezone
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied


class NarrativeForm(ModelForm):
    date_created = forms.DateField(widget=SelectDateWidget(years=range(timezone.now().year, timezone.now().year-110, -1)), required=False)
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'larger', 'onfocus': 'if($(this).val()==this.defaultValue){$(this).val("")};', 'onblur': 'if($(this).val()==""){$(this).val(this.defaultValue)};'}))  # default value moved to views.py

    def __init__(self, explorer, *args, **kwargs):
        super(NarrativeForm, self).__init__(*args, **kwargs)
        self.fields['experience'].queryset = explorer.experiences.all()

    def clean_date_created(self):
        date_created = self.cleaned_data.get('date_created')
        if not date_created:
            date_created = timezone.now()
        return date_created

    def clean_narrative(self):
        narrative = self.cleaned_data.get('narrative')
        if len(narrative) < 3:
            raise forms.ValidationError('Narrative needs a little more extrapolation')
        return narrative

    class Meta:
        model = Narrative
        exclude = ('gallery', 'author')
