from datetime import datetime

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from experiences.models import Experience

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
    Model for 'appreciating' function
    '''
    explorer = models.ForeignKey(get_user_model())
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_pk = models.TextField(_('object ID'), null=False)

    def __unicode__(self):
        return 'hurrah'


# To be modified to a class that will be neutral to whether the request is by
# the current owner/author and the recruit
class Request(models.Model):
    author = models.ForeignKey(get_user_model(), related_name='experience_author')
    recruit = models.ForeignKey(get_user_model(), related_name='experience_recruit')
    experience = models.ForeignKey(Experience)

    def __unicode__(self):
        return '{0} invitation'.format(self.experience)
