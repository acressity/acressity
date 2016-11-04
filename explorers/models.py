from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from itertools import chain
from django.conf import settings
from django.core.urlresolvers import reverse

from photologue.models import Gallery
from experiences.models import Experience
from acressity.utils import build_full_absolute_url


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

    def get_random(self, num=1):
        return self.order_by('?')[:num]


class Explorer(AbstractBaseUser):
    '''
    The term given to describe each logged user of the website.
    Each explorer has a unique trailname. This extends the
    Django User model.
    '''
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=60, null=False)
    trailname = models.CharField(
        max_length=55,
        null=True,
        blank=True,
        unique=True,
        help_text=_('A trailname is a short username or nickname given to each explorer of this website, able to be changed at any time. Inspired by the tradition common with Appalachian Trail hikers, you\'re encouraged to create a trailname that describes an aspect of your journey at the moment. It\'ll be displayed as John "<em>trailname</em>" Doe. It also allows others to find you by typing <code>acressity.com/<em>trailname</em></code>.')
    )
    gallery = models.OneToOneField(
        Gallery,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='story_gallery'
    )
    brief = models.TextField(null=True, blank=True, help_text=_('Short bio about you'))
    email = models.EmailField(
        max_length=254,
        null=False,
        blank=False,
        unique=True,
        help_text=_('Email addresses are used for resetting passwords and notifications. Privacy is protected and honored.')
    )
    birthdate = models.DateField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    notify = models.BooleanField(default=True)
    experiences = models.ManyToManyField(Experience, related_name='explorers')
    tracking_experiences = models.ManyToManyField(
        Experience,
        related_name='tracking_explorers',
        blank=True,
        help_text=_('Experiences that the explorer has chosen to track.')
    )
    featured_experience = models.ForeignKey(
        Experience,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='featured_experience',
        help_text=_('The experience that an explorer is currently featuring. Will be displayed on explorer\'s dash for easy accessibility and will be shown alongside explorer information for others to see.')
    )
    paypal_email_address = models.EmailField(
        null=True,
        blank=True,
        unique=True,
        help_text=_('Email address for your PayPal account. This is the email address to which donations by benefactors are made.')
    )

    objects = ExplorerManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'password']

    def __unicode__(self):
        return self.get_full_name()

    def model(self):
        return self.__class__.__name__

    def ordered_experiences(self):

        def sort_experience(experience):
            # Sort only by most recent public experience if not privileged
            # Keeps from revealing a private experience with recent activity
            if experience.narratives.count():
                if self in experience.explorers.all():
                    return experience.latest_narrative().date_created
                elif experience.public_narratives().count():
                    return experience.latest_public_narrative().date_created
            return experience.date_created

        if self.featured_experience:
            # We need to place the featured experience at front
            return list(chain([self.featured_experience], sorted(self.experiences.exclude(pk=self.featured_experience.pk).order_by('-date_created'), key=sort_experience, reverse=True)))
        return self.experiences.order_by('-date_created')

    def get_full_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

    def get_full_trailname(self):
        if self.trailname:
            return '{0} "{1}" {2}'.format(self.first_name, self.trailname, self.last_name)
        else:
            return self.get_full_name()

    @property
    def username(self):
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
        return sorted(self.experiences.exclude(title=self.featured_experience).exclude(narratives__isnull=True), key=lambda a: a.latest_narrative().date_created, reverse=True) + list(self.experiences.filter(narratives__isnull=True))  # Ugly...

    def top_five(self):
        return self.ordered_experiences()[:5]

    # Wanting to have only 3 to keep topbar dropdown less cluttered. Need top_five for backwards compatibility
    def top_three(self):
        return self.ordered_experiences()[:3]

    def latest_narrative(self):
        if self.narratives.exists():
            return self.narratives.latest('date_created')

    def get_absolute_url(self):
        # Despite the name, returns url relative to root
        return reverse('journey', args=[self.pk])

    def get_icon_url(self):
        if self.gallery.featured_photo:
            return self.gallery.featured_photo.get_icon_url()
        return '{0}/img/icons/explorer-icon-small.png'.format(settings.STATIC_URL)

    def get_thumbnail_url(self):
        if self.gallery and self.gallery.featured_photo:
            return self.gallery.featured_photo.get_thumbnail_url()
        return '{0}/img/icons/explorer-icon.png'.format(settings.STATIC_URL)

    def get_full_absolute_url(self):
        # Return the complete url with scheme and domain
        return build_full_absolute_url(self.get_absolute_url())
