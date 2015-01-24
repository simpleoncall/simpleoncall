from django.conf import settings
from pushbullet import PushBullet


def send_alert_pushbullet(alert, email):
    pb = PushBullet(settings.PUSHBULLET_ACCESS_TOKEN)
    title = 'new alert: %s' % (alert.title, )
    pb.push_link(title, 'http://127.0.0.1:8000/', body=alert.get_body(), email=email)
