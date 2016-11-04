from datetime import datetime

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.forms import ModelForm
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from support.models import PotentialExplorer
from django_comments_xtd.forms import XtdCommentForm


class CommentForm(XtdCommentForm):
    followup = forms.BooleanField(required=False,
                                  initial=True,
                                  label=_("Notify me about follow-up comments"))

    def __init__(self, *args, **kwargs):
        if 'comment' in kwargs:
            followup_suffix = ('_%d' % kwargs['comment'].pk)
        else:
            followup_suffix = ''
        super(CommentForm, self).__init__(*args, **kwargs)
        for field_name, field_obj in self.fields.items():
            if field_name == 'followup':
                field_obj.widget.attrs['id'] = 'id_followup%s' % followup_suffix
                continue
            field_obj.widget.attrs.update({'class': 'form-control'})
            if field_name == 'comment':
                field_obj.widget.attrs.pop('cols')
                field_obj.widget.attrs.pop('rows')
                field_obj.widget.attrs['placeholder'] = _('Your comment')
                field_obj.widget.attrs['style'] = "font-size: 1.1em"
            if field_name == 'url':
                field_obj.help_text = _('Optional')


class PotentialExplorerForm(ModelForm):
    # experience = forms.MultipleChoiceField()

    class Meta:
        model = PotentialExplorer
        exclude = ()

    # def __init__(self, explorer, *args, **kwargs):
    #     super(PotentialExplorerForm, self).__init__(*args, **kwargs)
    #     self.fields['experience'].queryset = explorer.experiences.all()

    # def clean_experience(self):
    #     experience = self.cleaned_data.get('experience')
    #     if not experience:
    #         raise forms.ValidationError('You must select an experience to invite this person to')
    #     return experience
