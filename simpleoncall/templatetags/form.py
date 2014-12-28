from django import template

register = template.Library()


def pop_default(l, d):
    if len(l):
        return l.pop(0)
    return d


class AlertSettingRowNode(template.Node):
    TYPE_OPTIONS = {
        'email': 'E-Mail',
        'sms': 'SMS',
        'voice': 'Voice',
    }

    def __init__(self, index, selected_type='email', selected_time=0, disabled=False):
        self.index = index
        self.type = selected_type
        self.time = selected_time
        self.disabled = disabled

    def render(self, context):
        disabled = 'disabled' if self.disabled else ''
        output = (
            '<div class="alert-setting-row %s">'
            '<select name="alert_type[%s]">'
        ) % (disabled, self.index, )

        for value, label in self.TYPE_OPTIONS.iteritems():
            selected = 'selected' if value == self.type else ''
            output += '<option value="%s" %s>%s</option>' % (value, selected, label)

        output += (
            '</select>'
            'After'
            '<input type="text" name="alert_time[%s]" value="%s" />'
            'Minutes'
            '</div>'
        ) % (self.index, self.time)

        return output


@register.tag('alert_setting_row')
def evil_icon(parser, token):
    parts = token.split_contents()
    parts.pop(0)
    index = pop_default(parts, 0)
    selected_type = pop_default(parts, 'email')
    selected_time = pop_default(parts, 0)
    disabled = bool(pop_default(parts, 0))
    return AlertSettingRowNode(index, selected_type, selected_time, disabled)
