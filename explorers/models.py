from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, UserManager
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from itertools import chain
from django.conf import settings
from django.core.urlresolvers import reverse

from photologue.models import Gallery
from experiences.models import Experience
from acressity.utils import build_full_absolute_url, get_site_domain
from benefaction.models import Campaign


class ExplorerManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **other_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        explorer = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **other_fields
        )
        explorer.set_password(password)
        explorer.save(using=self._db)
        return explorer

    def get_random(self, num=1):
        return self.order_by('?')[:num]


class Explorer(AbstractBaseUser):
    help_text=_('''
    The term given to describe each logged user of the website.
    Each explorer has a unique trailname. This extends the
    Django User model.
    ''')
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=60, null=False)
    trailname = models.CharField(
        max_length=55, null=True, blank=True, unique=True,
        help_text=_('''
            A trailname is an optional short username or nickname for the 
            explorers of this website, able to be changed at any time. Inspired 
            by the tradition common with Appalachian Trail hikers, you\'re 
            encouraged to create a trailname that describes an aspect of your 
            journey at the moment.<br />It\'ll be displayed as John "<em>trailname</em>" 
            Doe.<br />It also allows others to find you by typing 
            <code>{domain}/<em>trailname</em></code>.
        '''.format(domain=get_site_domain()))
    )
    gallery = models.OneToOneField(
        Gallery, null=True, blank=True,
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
        Experience, related_name='tracking_explorers', blank=True,
        help_text=_('Experiences that the explorer has chosen to track.')
    )
    featured_experience = models.ForeignKey(
        Experience, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='featured_experience',
        help_text=_('The experience that an explorer is currently featuring. Will be displayed on explorer\'s dash for easy accessibility and will be shown alongside explorer information for others to see.')
    )

    objects = ExplorerManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

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

    def get_absolute_url(self):
        return reverse('journey', args=[self.pk])

    def get_full_trailname(self):
        if self.trailname:
            return '{0} "{1}" {2}'.format(self.first_name, self.trailname, self.last_name)
        else:
            return self.get_full_name()

    @property
    def username(self):
        return self.get_full_name()

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

    def shelved_experiences(self):
        return sorted(self.experiences.exclude(title=self.featured_experience).exclude(narratives__isnull=True), key=lambda a: a.latest_narrative().date_created, reverse=True) + list(self.experiences.filter(narratives__isnull=True))  # Ugly...

    def top_five(self):
        return self.ordered_experiences()[:5]

    def top_three(self):
        return self.ordered_experiences()[:3]

    def latest_narrative(self):
        if self.narratives.exists():
            return self.narratives.latest('date_created')

    def get_benefaction_campaigns(self):
        return Campaign.objects.filter(experience__in=self.experiences.all())

    def has_payment_account(self):
        # True if explorer has any connected accounts
        return self.has_stripe_account()

    def has_stripe_account(self):
        return hasattr(self, 'stripe_account')

    def is_stripe_connected(self):
        return self.has_stripe_account() and not self.stripe_account.is_deauthorized

    def get_absolute_url(self):
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
