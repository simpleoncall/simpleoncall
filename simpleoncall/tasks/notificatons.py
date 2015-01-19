import logging

from celery import shared_task
from django.conf import settings

from simpleoncall.models import Alert, User
from simpleoncall.mail import send_alert_mail

logger = logging.getLogger(__name__)


@shared_task
def send_email_notification(user_id, alert_id):
    user = User.objects.get(id=user_id)
    alert = Alert.objects.get(id=alert_id)
    return send_alert_mail(alert, user.email)


@shared_task
def send_sms_notification(user_id, alert_id):
    if not settings.ALLOW_SMS:
        logger.warning('SMS Notifications are disabled')
        return


@shared_task
def send_voice_notification(user_id, alert_id):
    if not settings.ALLOW_VOICE:
        logger.warning('Voice Notifications are disabled')
        return
