from datetime import datetime
from experiences.models import Experience
from photologue.models import Gallery, Photo

from django.db import models
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator


class Narrative(models.Model):
    '''
    Term describing description of an aspect of an experience.
    Think of these as pages or sections within a chapter;
    they are the sustenance of the experience.
    Examples of narratives include an update, thought, plan,
    itinerary, journal entry, publication, ad infinitum...
    '''
    narrative = models.TextField()
    title = models.CharField(max_length=200, blank=True, null=True)
    experience = models.ForeignKey(Experience, related_name='narratives')
    author = models.ForeignKey(get_user_model(), related_name='narratives')
    date_created = models.DateTimeField(default=datetime.now, null=False)
    category = models.CharField(max_length=25, null=True, blank=True)
    gallery = models.OneToOneField(Gallery, on_delete=models.SET_NULL, null=True)

    def __unicode__(self):
        return self.title

    def model(self):
        return self.__class__.__name__

    def get_experience_author(self):
        return get_user_model().objects.get(pk=self.experience.author_id)

    def taste(self, chars=250):
        if len(self.narrative) > chars:
            return u'{0}...'.format(self.narrative[:chars])
        else:
            return self.narrative

    def is_author(self, request):
        if request.user.is_authenticated():
            if request.user.id == self.author_id:
                return True
            else:
                return False
        else:
            return False

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.narrative[:20]
        super(Narrative, self).save(*args, **kwargs)

    def get_next_narrative(self):
        try:
            narrative = self.get_next_by_date_created(experience_id=self.experience_id)
        except Narrative.DoesNotExist:
            narrative = None
        return narrative

    def get_previous_narrative(self):
        try:
            narrative = self.get_previous_by_date_created(experience_id=self.experience_id)
        except Narrative.DoesNotExist:
            narrative = None
        return narrative
