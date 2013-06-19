from datetime import datetime
from explorers.models import Explorer
from experiences.models import Experience

from django import forms
from django.forms import ModelForm, extras


class RegistrationForm(ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label='password1')
    password2 = forms.CharField(widget=forms.PasswordInput, label='password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if not password2:
            raise forms.ValidationError("You must confirm your password")
        if password1 != password2:
            raise forms.ValidationError("Your passwords do not match")
        return password2

    class Meta:
        model = Explorer
        exclude = ('experiences', 'last_login', 'date_joined', 'password')


class ExplorerForm(ModelForm):
    birthdate = forms.DateField(widget=forms.extras.widgets.SelectDateWidget(years=range(datetime.now().year-110, datetime.now().year-2)))

    def __init__(self, explorer, *args, **kwargs):
        super(ExplorerForm, self).__init__(*args, **kwargs)
        self.fields['featured_experience'].queryset = explorer.experiences.all()

    class Meta:
        model = Explorer
        exclude = ('experiences', 'password', 'gallery', 'date_joined', 'is_active', 'is_superuser', 'is_staff', 'last_login')


class ContactForm(forms.Form):
    email = forms.EmailField(label='Your Email')
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)
