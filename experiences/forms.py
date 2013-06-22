from django import forms
from django.forms import ModelForm
from django.shortcuts import get_object_or_404

from experiences.models import Experience
from photologue.models import Photo
from explorers.models import Explorer


class ExperienceForm(ModelForm):
    experience = forms.CharField(widget=forms.TextInput(attrs={'onclick': 'setUp(this);', 'class': 'larger'}), max_length=200)
    make_feature = forms.BooleanField(required=False, initial=False, help_text='Featuring an experience attaches the experience to the Dash for easy access and tells others that this is the experience you are actively pursuing.')
    # explorers = forms.ModelMultipleChoiceField(queryset=Explorer.objects.all())

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ExperienceForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Experience
        exclude = ('date_created', 'author', 'gallery', 'make_feature')


class ExperienceBriefForm(ModelForm):
    class Meta:
        model = Experience
        fields = ('brief',)


class ExperiencePhotoForm(ModelForm):
    class Meta:
        model = Photo
        exclude = ('title_slug',)

# class QuickExperience(forms.Form):
# 	experience = forms.CharField(max_length=200)
