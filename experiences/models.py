from django.utils import timezone
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password

from photologue.models import Gallery
from acressity.utils import embed_string
from paypal.standard.ipn.models import PayPalIPN


class ExperienceManager(models.Manager):
    def get_random(self, num=1):
        return self.order_by('?')[:num]


class Experience(models.Model):
    '''
    The term signifying a single venture, goal, wish, exploration,
    (ad infinitum) that an explorer has expressed as being willing
    of attaining. Think of these as the titles of chapters within
    a book about a journey.
    '''

    experience = models.CharField(max_length=255, null=False, help_text=_('Title of the experience.'))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='authored_experiences', help_text=_('Explorer who created the experience. Has the ability of sending requests to other explorers to become comrades in this experience.'))
    date_created = models.DateTimeField(default=timezone.now, null=False, blank=True)
    date_modified = models.DateTimeField(auto_now=True, help_text=_('Updated every time object saved'), null=True, blank=True)
    brief = models.TextField(blank=True, null=True, help_text=_('Written description of the experience to provide a little insight.'))
    status = models.CharField(max_length=160, null=True, blank=True, help_text=_('Optional short state of the experience at the moment.'))
    gallery = models.OneToOneField(Gallery, null=True, blank=True, on_delete=models.SET_NULL)  # I think I want to cascade delete into the gallery as well
    is_public = models.BooleanField(default=False, help_text=_('It is recommended to keep an experience private until you are ready to announce it to the world. Private experiences are only seen by its explorers and those providing a correct password if one is selected, so you can choose to share this experience with just a few people and make it public later if you\'d like.'))
    password = models.CharField(_('password'), max_length=128, null=True, blank=True, help_text=_('Submitting the correct password provides access to the experience if it is private as well as all of the private narratives.'))
    search_term = models.CharField(
        max_length=80, null=True, blank=True, unique=True,
        help_text=_('Short phrase or word identifying the experience, allows access by typing <code>http://acressity.com/your_search_term_here</code>. Needs to be unique and cannot be the same as another explorer\'s trailname')
    )
    accepts_paypal = models.BooleanField(
        default=False, null=False, blank=True,
        help_text=_('Check this box if you want to be able to accept PayPal donations from benefactors.')
    )
    benefactors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='benefactors',
        help_text=_('All those who have donated to this experience')
    )
    donations = models.ManyToManyField(
        PayPalIPN, blank=True, related_name='donations',
        help_text=_('All the donations made to this experience')
    )

    objects = ExperienceManager()

    def __init__(self, *args, **kwargs):
        # Allows the quicker check of whether or not a particular field has changed
        # Considering using this in the method controlling status of is_public
        super(Experience, self).__init__(*args, **kwargs)
        self.__original_is_public = self.is_public

    def __unicode__(self):
        if not self.is_public:
            return self.experience + ' (Private Experience)'
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
        return False

    def ordered_narratives(self):
        return self.narratives.order_by('-date_created')

    def comrades(self, request):
        return self.explorers.exclude(id=request.user.id)

    def create_gallery(self):
        gallery = Gallery(title=self.experience, content_type=ContentType.objects.get_for_model(Experience), object_pk=self.id, is_public=self.is_public)
        gallery.save()
        return gallery

    def get_galleries(self):
        object_list = []
        for narrative in self.narratives.all():
            if narrative.gallery:
                object_list.append(narrative.gallery)
        if self.gallery:
            object_list.append(self.gallery)
        return object_list

    def latest_narrative(self):
        if self.narratives.exists() and self.narratives.filter(is_public=True):
            return self.public_narratives().latest('date_created')

    def public_narratives(self):
        'Return an ordered queryset of all the public narratives in this experience'
        return self.ordered_narratives().filter(is_public=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def save(self, *args, **kwargs):
        # Feature for toggling the experience gallery being public
        # with the toggling of experience is_public
        if self.__original_is_public != self.is_public:
            if not self.is_public:
                for narrative in self.narratives.filter(is_public=True):
                    narrative.is_public = False
                    narrative.save()
            if self.gallery:
                self.gallery.is_public = self.is_public
                self.gallery.save()
        super(Experience, self).save(*args, **kwargs)

    def embedded_brief(self):
        return embed_string(self.brief)

    def donations_total(self):
        return sum([donation.payment_gross for donation in self.donations.all() if donation.payment_status == 'Completed'])


class FeaturedExperience(models.Model):
    experience = models.ForeignKey(Experience)
    date_featured = models.DateTimeField(default=timezone.now)

    objects = ExperienceManager()

    def __unicode__(self):
        return self.experience.experience
