from django.forms import ModelForm
from narratives.models import Narrative
from django import forms
from datetime import datetime, date
from django.utils import timezone
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied


class NarrativeForm(ModelForm):
    date_created = forms.DateField(widget=forms.extras.widgets.SelectDateWidget(years=range(datetime.now().year, datetime.now().year-110, -1)), required=False)

    def __init__(self, explorer, *args, **kwargs):
        super(NarrativeForm, self).__init__(*args, **kwargs)
        self.fields['experience'].queryset = explorer.experiences.all()

    # def clean_narrative(self):
    #     narrative = self.cleaned_data.get('narrative')
    #     if not narrative:
    #         raise forms.ValidationError('Narrative field can\'t be empty')

    def clean_date_created(self):
        date_created = self.cleaned_data.get('date_created')
        if not date_created:
            date_created = datetime.now()
        return date_created

    class Meta:
        model = Narrative
        exclude = ('gallery', 'author')
