import logging

from celery import shared_task
from django.conf import settings

from simpleoncall.models import Alert, User, AlertSetting, AlertType, EventStatus
from simpleoncall.mail import send_alert_mail

logger = logging.getLogger(__name__)


def send_alert_notifications(user, alert):
    if not user or not alert:
        return False

    if alert.status != EventStatus.OPEN:
        return False

    alert_settings = AlertSetting.objects.filter(user=user)
    if not alert_settings:
        setting = AlertSetting(time=0, type=AlertType.EMAIL, user=user)
        setting.save()
        alert_settings = [setting]

    for setting in alert_settings:
        time = setting.time * 60
        if setting.type == AlertType.EMAIL:
            send_email_notification.apply_async((user.id, alert.id), countdown=time)
        elif setting.type == AlertType.SMS:
            send_sms_notification.apply_async((user.id, alert.id), countdown=time)
        elif setting.type == AlertType.VOICE:
            send_voice_notification.apply_async((user.id, alert.id), countdown=time)


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
