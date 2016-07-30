import pickle

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_comments.signals import comment_was_posted
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from experiences.models import Experience
from notifications.models import Notification


# I'm not satisfied with this at the moment. I want to have a model that encompasses the ability to cheer (track) an arbitrary object (such as explorer or experience). Yet I don't want to have disorganized data in the db...
# Perhaps simply rename this to CheerExplorer to reduce ambiguity, and have experience 'support' be coordinated via TrackExperience model
class Cheer(models.Model):
    '''
    Model for 'following' function
    '''
    cheerer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='cheers_from')
    explorer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='cheers_for')
    date_cheered = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return '{0} is cheering for {1}'.format(self.explorer, self.cheerer)


class Hurrah(models.Model):
    '''
    Model for 'appreciating' function. No functionality atm
    '''
    explorer = models.ForeignKey(settings.AUTH_USER_MODEL)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_pk = models.TextField(_('object ID'), null=False)

    def __unicode__(self):
        return 'hurrah'


class InvitationRequest(models.Model):
    '''
    Model attempting to be fairly universal for the potential new relationship between two people. Author refers to the explorer who created the experience. Recruit is an existing explorer, and potential_explorer is a person not yet registered, but nonetheless with some sort of interest in the experience.
    '''
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='experience_author', null=False, help_text='The author of the experience. Able to be the explorer who invited the recruit or potential explorer, or the person who an existing explorer is contacting to become a part of the experience.')
    recruit = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='experience_recruit', null=True, blank=True, help_text='References an existing explorer potentially being added to experience.')
    potential_explorer = models.ForeignKey('PotentialExplorer', null=True, blank=True, help_text='References potential new user with little information for registration provided by invitation author.', related_name='invitation_request')
    date_created = models.DateTimeField(default=timezone.now)
    experience = models.ForeignKey(Experience, null=False)
    code = models.CharField(max_length=25, null=True, blank=True, help_text='Random code sent with the email in the url, used to confirm the uniqueness and identity of the invited explorer.')

    def __unicode__(self):
        return '{0} invitation'.format(self.experience)


class QuoteManager(models.Manager):
    def random(self):
        return self.order_by('?').first()


class Quote(models.Model):
    quote_datafile = 'support/data/quotes.dat'

    body = models.TextField(null=False, blank=False)
    author = models.CharField(max_length=100, null=False, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)

    objects = QuoteManager()

    CATEGORIES = (
        ('motivational', 'motivational'),
        ('inspirational', 'inspirational'),
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORIES,
        default=CATEGORIES[0][0]
    )

    @classmethod
    def load_quotes_from_data(cls, filename=quote_datafile):
        with open(filename, 'rb') as quote_file:
            try:
                return pickle.load(quote_file)
            except EOFError:
                return []

    @classmethod
    def write_quotes_to_data(cls, data, filename=quote_datafile):
        with open(filename, 'wb') as quote_file:
            pickle.dump(data, quote_file, -1)


class PotentialExplorer(models.Model):
    '''
    Model to represent a person being invited to be a part of an experience. Should be deleted based on reply or a timeout
    '''
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=60, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False,
            help_text='This information is used responsibly. It will only be used to send an invitation request and create their profile should they choose to join.')

    def __unicode__(self):
        return '{0} {1}: potential new explorer'.format(self.first_name, self.last_name)

    # def save():
    #     'Transform this model instance into new explorer, with related experience as current feature'
    #     pass


def comment_handler(sender, **kwargs):
    '''
    Handler function specifically designed to handle new comments being created
    '''

    comment = kwargs.pop('comment')
    # request = kwargs.pop('request')

    model = comment.content_object.model()
    recipients = []
    if model == 'Explorer':
        recipients.append(comment.content_object)
    elif model == 'Experience':
        recipients = comment.content_object.explorers.all()
    elif model == 'Narrative':
        recipients = comment.content_object.experience.explorers.all()
    elif model == 'Photo':
        recipients.append(comment.content_object.author)
        
    for recipient in recipients:
        newnotify = Notification(
            recipient=recipient,
            #sender=comment.user,
            verb='has posted a new note',
            actor_content_type=ContentType.objects.get_for_model(comment.user),
            actor_object_id=comment.user.pk,
            public=True,
            description=comment.comment,
            timestamp=timezone.now()
        )

        newnotify.save()

        if newnotify.recipient.notify:
            to = newnotify.recipient.email
            from_email = 'acressity@acressity.com'
            subject = 'New note on your Acressity journey'
            text_content = render_to_string('notifications/email.txt', {'notice': newnotify})
            html_content = render_to_string('notifications/email.html', {'notice': newnotify})
            message = EmailMultiAlternatives(subject, text_content, from_email, [to])
            message.attach_alternative(html_content, 'text/html')  # This will no longer be necessary in Django 1.7. Can be provided to send_mail as function parameter
            message.send()

comment_was_posted.connect(comment_handler)
