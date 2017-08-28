from django import forms
from django.forms import ModelForm


class ContactForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=54)
    message = forms.CharField(widget=forms.Textarea)


class ExtendedModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        # Remove `:` from suffix display default
        kwargs.setdefault('label_suffix', '')
        super(ExtendedModelForm, self).__init__(*args, **kwargs)

