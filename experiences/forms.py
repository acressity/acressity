from django import forms
from django.forms import ModelForm
from experiences.models import Experience
from photologue.models import Photo
from explorers.models import Explorer


class ExperienceForm(ModelForm):
    experience = forms.CharField(initial="New experience...", widget=forms.TextInput(attrs={'onclick': 'setUp(this);', 'class': 'larger'}), max_length=200)
    make_feature = forms.BooleanField(required=False, initial=False)
    # explorers = forms.ModelMultipleChoiceField(queryset=Explorer.objects.all())

    # def __init__(self, experience, *args, **kwargs):
    #     super(ExperienceForm, self).__init__(*args, **kwargs)
    #     self.fields['featured_photo'].queryset = experience.get_photos()

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
