from django import forms
from django.forms import ModelForm, extras
from django.conf import settings
from django.contrib import auth

from datetime import datetime
from explorers.models import Explorer
from experiences.models import Experience


class RegistrationForm(ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'onblur': 'check_password1()'}), label='password1')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'onkeyup': 'check_password2()'}), label='password2')
    first_name = forms.CharField(widget=forms.TextInput(attrs={'onblur': 'say_hello();'}))
    trailname = forms.CharField(widget=forms.TextInput(attrs={'onblur': 'check_trailname();'}))

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if not password2:
            raise forms.ValidationError('You must confirm your password')
        if password1 != password2:
            raise forms.ValidationError('Your passwords do not match')
        if len(password2) < settings.MIN_PASSWORD_LEN:
            raise forms.ValidationError('Password must be at least {0} characters'.format(settings.MIN_PASSWORD_LEN))
        return password2

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if len(first_name) < 2:
            raise forms.ValidationError('Name too short')
        return first_name

    # def clean_trailname(self):
    #     return self.cleaned_data.get('trailname', None)

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
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=54)
    subject = forms.CharField(max_length=155)
    message = forms.CharField(widget=forms.Textarea)


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput())
    new_password1 = forms.CharField(widget=forms.PasswordInput())
    new_password2 = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        new_password2 = self.cleaned_data.get('new_password2')
        new_password1 = self.cleaned_data.get('new_password1')
        if len(new_password2) < settings.MIN_PASSWORD_LEN:
            raise forms.ValidationError('Password must be at least {0} characters'.format(settings.MIN_PASSWORD_LEN))
        if new_password2 != new_password1:
            raise forms.ValidationError('Your newly chosen passwords did not match')
