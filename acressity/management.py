# Suggested by django-notification "automatic notice type creation"

from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _

if "notification" in settings.INSTALLED_APPS:
    from notification import models as n

    def create_notice_types(app, created_models, verbosity, **kwargs):
        n.create_notice_type("friends_invite", _("Invitation Received"), _("you have received an invitation"))
        n.create_notice_type("friends_accept", _("Acceptance Received"), _("an invitation you sent has been accepted"))

    signals.post_syncdb.connect(create_notice_types, sender=n)
else:
    print "Skipping creation of NoticeTypes as notification app not found"
