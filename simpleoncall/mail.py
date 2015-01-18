from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string


def send_messages(messages):
    connection = mail.get_connection()
    return connection.send_messages(messages)


def send_invite_mail(invites):
    messages = []
    for invite in invites:
        messages.append(InviteEmailMessage(invite))
    return send_messages(messages)


def send_alert_mail(alert, recipient):
    return send_messages([AlertStatusEmailMessage(alert, recipient)])


class InviteEmailMessage(mail.EmailMultiAlternatives):
    def __init__(self, invite):
        subject = 'Invited to SimpleOnCall team %s' % (invite.team.name, )
        text_body = render_to_string('mail/invite.txt', {'invite': invite})
        html_body = render_to_string('mail/invite.html', {'invite': invite})
        super(InviteEmailMessage, self).__init__(
            subject, text_body, settings.EMAIL_FROM_ADDRESS, [invite.email]
        )
        self.attach_alternative(html_body, 'text/html')


class AlertStatusEmailMessage(mail.EmailMultiAlternatives):
    def __init__(self, alert, recipient):
        subject = 'New Alert %s' % (alert.title, )
        text_body = render_to_string('mail/alert.txt', {'alert': alert})
        html_body = render_to_string('mail/alert.html', {'alert': alert})
        super(AlertStatusEmailMessage, self).__init__(
            subject, text_body, settings.EMAIL_FROM_ADDRESS, [recipient]
        )
        self.attach_alternative(html_body, 'text/html')
