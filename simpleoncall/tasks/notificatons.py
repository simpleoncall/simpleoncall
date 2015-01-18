from celery import shared_task

from simpleoncall.models import Alert, User
from simpleoncall.mail import send_alert_mail


@shared_task
def send_email_notification(user_id, alert_id):
    user = User.objects.get(id=user_id)
    alert = Alert.objects.get(id=alert_id)
    return send_alert_mail(alert, user.email)


@shared_task
def send_sms_notification(user_id, alert_id):
    pass


@shared_task
def send_voice_notification(user_id, alert_id):
    pass
