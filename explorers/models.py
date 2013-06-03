from photologue.models import Gallery
from datetime import datetime
from experiences.models import Experience

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class ExplorerManager(BaseUserManager):
    def create_user(self, first_name, last_name, trailname, password):
        if not trailname:
            # Make unique trailname, as close to the user's real name as possible
            # Will need to be modified to ensure uniqueness...
            trailname = '{0}_{1}'.format(first_name, last_name)
        user = self.model(
            trailname=trailname,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class Explorer(AbstractBaseUser):
    '''
    The term given to describe each logged user of the website.
    Each explorer has a unique trailname. This extends the Explorer
    from the Django User model.
    '''
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    trailname = models.CharField(max_length=50, unique=True, db_index=True, help_text='The nickname given to each explorer of this website, inspired by the tradition common with Appalachian Trail hikers. Explorers are encouraged to create a trailname that describes an aspect of their journey at the moment.')
    gallery = models.OneToOneField(Gallery, null=True, blank=True, on_delete=models.SET_NULL, related_name='story_gallery')
    brief = models.TextField(null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    date_joined = models.DateTimeField(default=datetime.now)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    experiences = models.ManyToManyField(Experience, related_name='explorers')
    featured_experience = models.ForeignKey(Experience, null=True, blank=True, on_delete=models.SET_NULL, related_name='featured_experience')  # Consider altering this to keep from having no experience featured...?

    objects = ExplorerManager()

    USERNAME_FIELD = 'trailname'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'password']

    def __unicode__(self):
        return self.get_full_name()

    def model(self):
        return self.__class__.__name__

    def ordered_experiences(self):
        return sorted(self.experiences.exclude(narratives__isnull=True), key=lambda a: a.latest_narrative().date_created, reverse=True) + list(self.experiences.filter(narratives__isnull=True))  # Ugly...

    def get_full_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.trailname

    def cheering_for(self):
        return [c.explorer for c in self.cheers_from.all()]

    def cheerers(self):
        return [c.cheerer for c in self.cheers_for.all()]

    def shelved_experiences(self):
        return sorted(self.experiences.exclude(experience=self.featured_experience).exclude(narratives__isnull=True), key=lambda a: a.latest_narrative().date_created, reverse=True) + list(self.experiences.filter(narratives__isnull=True))  # Ugly...

    def top_five(self):
        return list(sorted(self.experiences.exclude(narratives__isnull=True), key=lambda a: a.latest_narrative().date_created, reverse=True) + list(self.experiences.filter(narratives__isnull=True)))[:5]  # Ugly...

    def latest_narrative(self):
        if self.narratives.exists():
            return self.narratives.latest('date_created')


# To be modified to a class that will be neutral to whether the request is by
# the current owner/author and the recruit
class Request(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='experience_author')
    recruit = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='experience_recruit')
    experience = models.ForeignKey(Experience)

    def __unicode__(self):
        return '{0} invitation'.format(self.experience)
