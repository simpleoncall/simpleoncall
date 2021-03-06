import logging

from celery import shared_task
from django.conf import settings

from simpleoncall.models import Alert, User, NotificationSetting, NotificationType, EventStatus
from simpleoncall.mail import send_alert_mail
from simpleoncall.push import send_alert_pushbullet

logger = logging.getLogger(__name__)


def send_alert_notifications(user, alert):
    if not user or not alert:
        return False

    if alert.status != EventStatus.OPEN:
        return False

    notification_settings = NotificationSetting.objects.filter(user=user)
    if not notification_settings:
        setting = NotificationSetting(time=0, type=NotificationType.EMAIL, user=user)
        setting.save()
        notification_settings = [setting]

    for setting in notification_settings:
        time = setting.time * 60
        if setting.type == NotificationType.EMAIL:
            send_email_notification.apply_async((user.id, alert.id), countdown=time)
        elif setting.type == NotificationType.SMS:
            send_sms_notification.apply_async((user.id, alert.id), countdown=time)
        elif setting.type == NotificationType.VOICE:
            send_voice_notification.apply_async((user.id, alert.id), countdown=time)
        elif setting.type == NotificationType.PUSHBULLET:
            send_pushbullet_notification.apply_async((user.id, alert.id), countdown=time)


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


@shared_task
def send_pushbullet_notification(user_id, alert_id):
    if not settings.PUSHBULLET_ACCESS_TOKEN:
        logger.warning('Pushbullet Notifications are disabled')
        return
    user = User.objects.get(id=user_id)
    alert = Alert.objects.get(id=alert_id)
    return send_alert_pushbullet(alert, user.email)
