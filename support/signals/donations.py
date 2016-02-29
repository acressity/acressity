from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

from explorers.models import Explorer
from paypal.standard.models import ST_PP_COMPLETED, ST_PP_DECLINED, ST_PP_DENIED, ST_PP_EXPIRED, ST_PP_FAILED, \
    ST_PP_UNCLEARED
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received
from notifications import notify


failed_paypal_statuses = [
    ST_PP_DECLINED, ST_PP_DENIED, ST_PP_EXPIRED, ST_PP_FAILED, ST_PP_UNCLEARED
]


@receiver(valid_ipn_received)
@receiver(invalid_ipn_received)
def handle_paypal_signals(sender, **kwargs):
    # Argument needs to come in named as sender
    paypal_ipn_object = sender
    recipient = get_user_model().objects.get(paypal_email_address=paypal_ipn_object.business)

    try:
        benefactor = get_user_model().objects.get(paypal_email_address=paypal_ipn_object.payer_email)
    except ObjectDoesNotExist:
        benefactor = paypal_ipn_object.payer_email

    item = get_item(paypal_ipn_object)
    if paypal_ipn_object.payment_status == ST_PP_COMPLETED and not paypal_ipn_object.flag:
        # Notify both users of the successful transaction
        if item.model() == 'Experience':
            item.donations.add(paypal_ipn_object)
            notification_verb = 'has donated ${0} to your experience {1}.'.format(
                paypal_ipn_object.payment_gross, item)
            if paypal_ipn_object.memo:
                notification_verb += ' With a memo: "{0}"'.format(paypal_ipn_object.memo)
            for explorer in item.explorers.all():
                notify.send(
                    sender=benefactor, recipient=explorer,
                    verb=notification_verb
                )
            if isinstance(benefactor, Explorer):
                notify.send(
                    sender=recipient, recipient=benefactor,
                    verb='has successfully received your donation of ${0} to their experience {1}'.format(paypal_ipn_object.payment_gross, item))
    else:
        # Remove the user from benefactor status (hopefully only temporarily) and notify the users involved
        if paypal_ipn_object.payment_status in failed_paypal_statuses:
            if isinstance(benefactor, Explorer):
                item.benefactors.remove(benefactor)
                notify.send(
                    sender=recipient, recipient=benefactor,
                    verb='has failed to receive your donation of ${0} to their experience {1}.'
                    'Please try again.'.format(paypal_ipn_object.payment_gross, item)
                )


def get_item(paypal_ipn_object):
    # item_name and item_number attributes hold the item model and item pk
    # respectively. Coded in support.views
    item_pk = int(paypal_ipn_object.item_number)
    item_model_name = paypal_ipn_object.item_name.split(':')[0]
    item_content_type = ContentType.objects.get(model=item_model_name)
    return item_content_type.get_object_for_this_type(pk=item_pk)
