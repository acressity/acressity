from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _


# Model for 'following' function
class Cheer(models.Model):
    cheerer = models.ForeignKey(get_user_model(), related_name='cheers_from')
    explorer = models.ForeignKey(get_user_model(), related_name='cheers_for')
    date_cheered = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return '{0} is cheering for {1}'.format(self.explorer, self.cheerer)


# Model for 'appreciating' function
class Hurrah(models.Model):
    explorer = models.ForeignKey(get_user_model())
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_pk = models.TextField(_('object ID'), null=False)

    def __unicode__(self):
        return 'hurrah'
