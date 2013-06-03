from datetime import datetime
from photologue.models import Photo, Gallery

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

# @receiver(m2m_changed, sender=Narrative)
# def experience_handler(sender, **kwargs):
# 	pass


class ExperienceManager(models.Manager):
    def get_random(self, num=1):
        return self.order_by('?')[:num]


class Experience(models.Model):
    '''
    The term signifying a single venture, goal, wish, exploration,
    (ad infinitum) that an explorer has expressed as being willing
    of attaining. Think of these as the titles of chapters within
    a book about your journey.
    '''

    experience = models.CharField(max_length=200)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='authored_experiences')
    date_created = models.DateTimeField(default=datetime.now)
    brief = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=25, null=True, blank=True)
    gallery = models.OneToOneField(Gallery, null=True, blank=True, on_delete=models.SET_NULL)

    objects = ExperienceManager()

    def __unicode__(self):
        return self.experience

    def __str__(self):
        return self.__unicode__()

    def model(self):
        return self.__class__.__name__

    def get_photos(self):
        queryset = self.gallery.photos.none()
        if self.gallery:
            queryset = queryset | self.gallery.photos.all()
        narrative_galleries = [narrative.gallery for narrative in self.narratives.all() if narrative.gallery]
        for gallery in narrative_galleries:
            queryset = queryset | gallery.photos.all()
        return queryset

    def is_author(self, request):
        if request.user.is_authenticated():
            if request.user == self.author:
                return True
            else:
                return False
        else:
            return False

    def is_comrade(self, request):
        if request.user.is_authenticated():
            if request.user in self.explorers.all():
                return True
            else:
                return False
        else:
            return False

    def ordered_narratives(self):
        return self.narratives.order_by('-date_created')

    def get_galleries(self):
        object_list = []
        for narrative in self.narratives.all():
            if narrative.gallery:
                object_list.append(narrative.gallery)
        if self.gallery:
            object_list.append(self.gallery)
        return object_list

    def latest_narrative(self):
        if self.narratives.exists():
            return self.narratives.latest('date_created')


class FeaturedExperience(models.Model):
    experience = models.ForeignKey(Experience)
    date_featured = models.DateTimeField(default=datetime.now)

    objects = ExperienceManager()

    def __unicode__(self):
        return self.experience.experience
