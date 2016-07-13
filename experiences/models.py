from django.utils import timezone
from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import curry
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
    date_created = models.DateTimeField(default=timezone.now, null=False,
            blank=True, help_text=_('''The day you committed to achieving this
                experience. Leave blank for today'''))
    date_modified = models.DateTimeField(auto_now=True, help_text=_('Updated every time object saved'), null=True, blank=True)
    brief = models.TextField(blank=True, null=True, help_text=_('Central to making this experience more real, write a brief about what this experience entails. What are your hopes and aspirations? This is a way for others to understand your intention and for you to get some clarity.'))
    status = models.CharField(max_length=160, null=True, blank=True, help_text=_('Optional short state of the experience at the moment.'))
    gallery = models.OneToOneField(Gallery, null=True, blank=True, on_delete=models.SET_NULL)  # I think I want to cascade delete into the gallery as well
    is_public = models.BooleanField(default=False, help_text=_('It is recommended to keep an experience private until you are ready to announce it to the world. Private experiences are only seen by its explorers and those providing a correct password if one is selected, so you can choose to share this experience with just a few people and make it public later if you\'d like.'))
    percent_fulfilled = models.IntegerField(default=0,
            validators=[MinValueValidator(0), MaxValueValidator(100)],
            blank=True,
            help_text=_('''The fraction complete the experience is, from beginning
            to end. Rough estimates are fine if there\'s no clear way to
            determine this percentage'''))
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
    intended_completion_date = models.DateField(blank=True,
            null=True, help_text=_('''Optional date by which you intend to be
                finished. Take care if choosing to set a date, as this feature
                can be demotivating if used improperly. Leave blank if you do
                not want this to be displayed or if not relevant.''')
    )

    objects = ExperienceManager()

    def __init__(self, *args, **kwargs):
        # Allows the quicker check of whether or not a particular field has changed
        # Considering using this in the method controlling status of is_public
        super(Experience, self).__init__(*args, **kwargs)
        self.__original_is_public = self.is_public

        # Add method names for accessing help text from class object instances
        for field in self._meta.fields:
            method_name = 'get_{0}_help_text'.format(field.name)
            # Use curry to create the method with a pre-defined argument
            curried_method = curry(self._get_help_text, field=field.name)
            # Add method to instance of class
            setattr(self, method_name, curried_method)

    def __unicode__(self):
        return self.experience

    def __str__(self):
        return self.__unicode__()

    def model(self):
        return self.__class__.__name__

    def _get_help_text(self, field):
        for f in self._meta.fields:
            if field == f.name:
                return f.help_text

    def get_photos(self):
        queryset = self.gallery.photos.none()
        if self.gallery:
            queryset = queryset | self.gallery.photos.all()
        narrative_galleries = [narrative.gallery for narrative in self.narratives.all() if narrative.gallery]
        for gallery in narrative_galleries:
            queryset = queryset | gallery.photos.all()
        return queryset

    def is_author(self, request):
        return request.user.is_authenticated() and request.user == self.author

    def is_comrade(self, request):
        return request.user.is_authenticated() and request.user in self.explorers.all()

    def comrades(self, request):
        return self.explorers.exclude(id=request.user.id)

    def is_fulfilled(self):
        return self.percent_fulfilled == 100

    def create_gallery(self):
        gallery = Gallery(title=self.experience, content_type=ContentType.objects.get_for_model(Experience), object_pk=self.id, is_public=self.is_public)
        gallery.save()
        return gallery

    def get_galleries(self):
        galleries = [narrative.gallery for narrative in self.narratives.all()
                if narrative.gallery]
        if self.gallery:
            galleries.append(self.gallery)
        return galleries

    def ordered_narratives(self):
        return self.narratives.order_by('-date_created')

    def public_narratives(self):
        'Return an ordered queryset of all the public narratives in this experience'
        return self.ordered_narratives().filter(is_public=True)

    def latest_public_narrative(self):
        return self.narratives.filter(is_public=True).latest('date_created')

    def latest_narrative(self):
        return self.narratives.latest('date_created')

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
