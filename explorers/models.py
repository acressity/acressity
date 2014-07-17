from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.signals import request_finished

from photologue.models import Gallery
from datetime import datetime
from experiences.models import Experience


class ExplorerManager(BaseUserManager):
    # Following is currently not being used
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
    last_name = models.CharField(max_length=60, null=False)
    trailname = models.CharField(max_length=50, null=True, blank=True, unique=True, help_text='A trailname is a short username or nickname given to each explorer of this website, able to be changed at any time. Inspired by the tradition common with Appalachian Trail hikers, you are encouraged to create a trailname that describes an aspect of your journey at the moment. It also allows others to find you by typing acressity.com/<em>trailname</em>')
    gallery = models.OneToOneField(Gallery, null=True, blank=True, on_delete=models.SET_NULL, related_name='story_gallery')
    brief = models.TextField(null=True, blank=True, help_text='Short bio about you')
    email = models.EmailField(max_length=254, null=False, blank=False, unique=True, help_text='Email addresses are used for resetting passwords and creating new narratives via email.')
    birthdate = models.DateField(null=True, blank=True)
    date_joined = models.DateTimeField(default=datetime.now)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    notify = models.BooleanField(default=True)
    experiences = models.ManyToManyField(Experience, related_name='explorers')
    tracking_experiences = models.ManyToManyField(Experience, related_name='tracking_explorers', blank=True, null=True, help_text='Experiences that the explorer has chosen to track.')
    featured_experience = models.ForeignKey(Experience, null=True, blank=True, on_delete=models.SET_NULL, related_name='featured_experience', help_text='The experience that an explorer is currently featuring. Will be displayed on explorer\'s dash for easy accessibility and will be shown alongside explorer information for others to see.')

    objects = ExplorerManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'password']

    def __unicode__(self):
        return self.get_full_name()

    def model(self):
        return self.__class__.__name__

    def ordered_experiences(self):
        from itertools import chain

        def sort_experience(experience):
            if experience.latest_narrative():
                return experience.latest_narrative().date_created
            else:
                return experience.date_created

        return list(chain(self.experiences.filter(experience=self.featured_experience), sorted(self.experiences.exclude(experience=self.featured_experience).order_by('-date_created'), key=sort_experience, reverse=True)))

    def get_full_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

    def get_full_trailname(self):
        if self.trailname:
            return '{0} "{1}" {2}'.format(self.first_name, self.trailname, self.last_name)
        else:
            return self.get_full_name()

    # Following not used, but I think it's necessary with the extended user model?
    def get_short_name(self):
        return self.first_name

    def cheering_for(self):
        return [c.explorer for c in self.cheers_from.all()]

    def top_cheerers(self):
        return self.cheering_for()[:3]

    def cheerers(self):
        return [c.cheerer for c in self.cheers_for.all()]

    def public_experiences(self):
        return self.experiences.filter(is_public=True)

    def private_experiences(self):
        return self.experiences.filter(is_public=False)

    # Don't think this is currently being used...phasing it out in favor of returning all experiences in a sorted fashion
    def shelved_experiences(self):
        return sorted(self.experiences.exclude(experience=self.featured_experience).exclude(narratives__isnull=True), key=lambda a: a.latest_narrative().date_created, reverse=True) + list(self.experiences.filter(narratives__isnull=True))  # Ugly...

    def top_five(self):
        return self.ordered_experiences()[:5]

    def latest_narrative(self):
        if self.narratives.exists():
            return self.narratives.latest('date_created')
