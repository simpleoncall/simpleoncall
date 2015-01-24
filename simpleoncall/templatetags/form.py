from django import template

from simpleoncall.models import NotificationType
from simpleoncall.templatetags.icons import EvilIconNode

register = template.Library()


def pop_default(l, d):
    if len(l):
        return l.pop(0)
    return d


class NotificationSettingRowNode(template.Node):
    TYPE_OPTIONS = {
        NotificationType.EMAIL: 'E-Mail',
        NotificationType.SMS: 'SMS',
        NotificationType.VOICE: 'Voice',
        NotificationType.PUSHBULLET: 'Pushbullet',
    }

    def __init__(self, id, selected_type='email', selected_time=0, disabled=False):
        self.id = id
        self.type = selected_type
        self.time = selected_time
        self.disabled = disabled

    def render(self, context=None):
        disabled = 'disabled' if self.disabled else ''
        output = (
            '<div class="alert-setting-row %s" data-id="%s">'
            '<select name="alert_type">'
        ) % (disabled, self.id)

        for value, label in self.TYPE_OPTIONS.iteritems():
            selected = 'selected' if value == self.type else ''
            output += '<option value="%s" %s>%s</option>' % (value, selected, label)

        remove_icon = EvilIconNode('ei-minus')
        output += (
            '</select>'
            'After'
            '<input type="text" name="alert_time" value="%s" maxlength="3" />'
            'Minutes'
            '<span class="remove-alert-row">'
            '%s'
            '</span>'
            '</div>'
        ) % (self.time, remove_icon.render())

        return output


@register.tag('notification_setting_row')
def notification_setting_row(parser, token):
    parts = token.split_contents()
    parts.pop(0)
    index = pop_default(parts, 0)
    selected_type = pop_default(parts, 'email')
    selected_time = pop_default(parts, 0)
    disabled = bool(pop_default(parts, 0))
    return NotificationSettingRowNode(index, selected_type, selected_time, disabled)


@register.filter('notification_setting_row')
def notification_setting_filter(alert):
    return NotificationSettingRowNode(alert.id, alert.type, alert.time, 0).render()
