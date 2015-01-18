from __future__ import absolute_import

from celery import shared_task


@shared_task
def send_email_notification(user_id, alert_id):
    pass


@shared_task
def send_sms_notification(user_id, alert_id):
    pass


@shared_task
def send_voice_notification(user_id, alert_id):
    pass
