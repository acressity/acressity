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
    narrative = models.TextField(help_text='The content of narrative. Where information regarding any thoughts, feelings, updates, etc can be added.')
    title = models.CharField(max_length=200, blank=True, null=True, help_text='Title of the narrative. If none given, defaults to date created.')
    experience = models.ForeignKey(Experience, related_name='narratives')
    author = models.ForeignKey(get_user_model(), related_name='narratives', null=False)
    date_created = models.DateTimeField(default=datetime.now, null=False, blank=True)
    date_modified = models.DateTimeField(auto_now=True, help_text='Updated every time object saved')
    category = models.CharField(max_length=50, null=True, blank=True, help_text='Optional information used to classify and order the narratives within the experience.')
    gallery = models.OneToOneField(Gallery, on_delete=models.SET_NULL, null=True)
    is_public = models.BooleanField(default=True, help_text='Public narratives will be displayed in the default views. Private ones are only seen by yourself.')

    class Meta:
        #ordering = ['category']
        get_latest_by = 'date_created'

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
            self.title = datetime.now().strftime('%B %d, %Y')
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

    def parse_for_embed(self):
        '''
        Build in progress.
        Attempts to take the narrative.narrative attribute and check for significant strings.
        Specific uses:
            -embedding video via YouTube API if youtube.com exists
            -link to external websites if explorer submits string for link
            -Possibly display an image from the gallery with simple code

        Extremely primitive, but that's fine at the moment.
        '''

        import re
        from urlparse import urlparse

        # Seems so incredibly inefficient at the moment...
        if re.search('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', self.narrative):
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', self.narrative)
            for url in urls:
                parsed_url = urlparse(url)
                if 'youtube' in parsed_url.netloc.lower():
                    if 'v=' in parsed_url.query.lower():
                        code_start = re.search('v=', parsed_url.query).end()
                        if '&' in parsed_url.query:
                            code_end = parsed_url.query.find('&', re.search('v=', parsed_url.query).end())
                        else:
                            code_end = None
                        code = parsed_url.query[code_start:code_end]
                        return '<iframe width="560" height="315" src="http://www.youtube.com/embed/{0}" frameborder="0" allowfullscreen></iframe>'.format(code)
