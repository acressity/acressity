from django.forms import ModelForm
from narratives.models import Narrative
from django import forms
from datetime import datetime, date
from django.utils import timezone


class NarrativeForm(ModelForm):
    date_created = forms.DateField(widget=forms.extras.widgets.SelectDateWidget(years=range(datetime.now().year, datetime.now().year-110)))

    def __init__(self, explorer, *args, **kwargs):
        super(NarrativeForm, self).__init__(*args, **kwargs)
        self.fields['experience'].queryset = explorer.experiences.all()

    class Meta:
        model = Narrative
        exclude = ('gallery', 'author')


