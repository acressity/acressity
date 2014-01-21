from datetime import datetime

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.signals import comment_was_posted

from experiences.models import Experience
from notifications.models import Notification


# I'm not satisfied with this at the moment. I want to have a model that encompasses the ability to cheer (track) an arbitrary object (such as explorer or experience). Yet I don't want to have disorganized data in the db...
# Perhaps simply rename this to CheerExplorer to reduce ambiguity, and have experience 'support' be coordinated via TrackExperience model
class Cheer(models.Model):
    '''
    Model for 'following' function
    '''
    cheerer = models.ForeignKey(get_user_model(), related_name='cheers_from')
    explorer = models.ForeignKey(get_user_model(), related_name='cheers_for')
    date_cheered = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return '{0} is cheering for {1}'.format(self.explorer, self.cheerer)


# Blahhhhh... This is being changed to a ManyToMany relationship in the explorer model. Doesn't work as well this way, though I would like to have the date_tracked information.
# class TrackExperience(models.Model):
#     experience = models.ForeignKey(Experience)
#     explorer = models.ForeignKey(get_user_model(), related_name='tracking_experiences')
#     date_tracked = models.DateTimeField(default=datetime.now)

#     def __unicode__(self):
#         return self.experience.experience


class Hurrah(models.Model):
    '''
    Model for 'appreciating' function. No functionality atm
    '''
    explorer = models.ForeignKey(get_user_model())
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_pk = models.TextField(_('object ID'), null=False)

    def __unicode__(self):
        return 'hurrah'


class InvitationRequest(models.Model):
    '''
    Model attempting to be fairly universal for the potential new relationship between two people. Author refers to the explorer who created the experience. Recruit is an existing explorer, and potential_explorer is a person not yet registered, but nonetheless with some sort of interest in the experience.
    '''
    author = models.ForeignKey(get_user_model(), related_name='experience_author', null=False, help_text='The author of the experience. Able to be the explorer who invited the recruit or potential explorer, or the person who an existing explorer is contacting to become a part of the experience.')
    recruit = models.ForeignKey(get_user_model(), related_name='experience_recruit', null=True, blank=True, help_text='References an existing explorer potentially being added to experience.')
    potential_explorer = models.ForeignKey('PotentialExplorer', null=True, blank=True, help_text='References potential new user with little information for registration provided by invitation author.', related_name='invitation_request')
    date_created = models.DateTimeField(default=datetime.now)
    experience = models.ForeignKey(Experience, null=False)
    code = models.CharField(max_length=25, null=True, blank=True, help_text='Random code sent with the email in the url, used to confirm the uniqueness and identity of the invited explorer.')

    def __unicode__(self):
        return '{0} invitation'.format(self.experience)


class PotentialExplorer(models.Model):
    '''
    Model to represent a person being invited to be a part of an experience. Should be deleted based on reply or a timeout
    '''
    first_name = models.CharField(max_length=30, null=False, blank=False)
    last_name = models.CharField(max_length=30, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False, help_text='This information is used responsibly. It will only be used to send an invitation request.')

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

    o = comment.content_object.model()
    if o == 'Explorer':
        recipient = comment.content_object
    elif o == 'Experience':
        recipient = comment.content_object.author  # This should eventually handle all explorers of the experience
    elif o == 'Narrative':
        recipient = comment.content_object.author
    newnotify = Notification(
        recipient=recipient,
        #sender=comment.user,
        verb='has posted a new note',
        actor_content_type=ContentType.objects.get_for_model(comment.user),
        actor_object_id=comment.user.pk,
        public=True,
        description=comment.comment,
        timestamp=datetime.now()
    )

    newnotify.save()


comment_was_posted.connect(comment_handler)
