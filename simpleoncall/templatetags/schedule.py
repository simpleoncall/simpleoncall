from django import template

from simpleoncall.templatetags.gravatar import gravatar_url

register = template.Library()


class ScheduleTableNode(template.Node):
    def __init__(self, schedule):
        self.schedule = schedule

    def open_table(self):
        return '<table class="pure-table pure-table pure-table-bordered pure-table-striped">'

    def close_table(self):
        return '</table>'

    def render(self, context=None):
        output = self.open_table()

        output += ScheduleHeaderNode(self.schedule.get('labels', [])).render()
        output += ScheduleUsersNode(self.schedule.get('users', [])).render()

        output += self.close_table()
        return output


class ScheduleHeaderNode(template.Node):
    def __init__(self, labels):
        self.labels = labels

    def open_header(self):
        return '<thead><tr>'

    def close_header(self):
        return '</tr></thead>'

    def header_cell(self, short_name, long_name):
        return ''.join([
            '<th>',
            '<span class="short-name">', short_name, '</span>',
            '<span class="long-name">', long_name, '</span>',
            '</th>',
        ])

    def render(self, context=None):
        output = self.open_header()

        # add an empty header for the user info
        output += self.header_cell('', '')
        for label in self.labels:
            output += self.header_cell(**label)

        output += self.close_header()
        return output


class ScheduleUsersNode(template.Node):
    def __init__(self, users):
        self.users = users

    def open_body(self):
        return '<tbody>'

    def close_body(self):
        return '</tbody>'

    def render(self, context=None):
        output = self.open_body()

        for user_data in self.users:
            output += ScheduleUserRowNode(**user_data).render()

        output += self.close_body()
        return output


class ScheduleUserRowNode(template.Node):
    def __init__(self, user, schedule):
        self.user = user
        self.schedule = schedule

    def open_row(self):
        return '<tr>'

    def close_row(self):
        return '</tr>'

    def user_info(self):
        return ''.join([
            '<td>',
            '<div class="pure-g">',
            '<div class="pure-u-1 pure-u-lg-1-5">', gravatar_url(self.user.email), '</div>',
            '<div class="pure-u-1 pure-u-lg-4-5">',
            '<div class="user-full-name pure-u-1 pure-u-lg-4-5">', self.user.get_full_name(), '</div>',
            '<div class="user-email pure-u-1 pure-u-lg-4-5">', self.user.email, '</div>',
            '</div>',
            '</div>',
            '</td>',
        ])

    def schedule_cell(self, class_name):
        return '<td class="%s"></td>' % (class_name, )

    def render(self, context=None):
        output = self.open_row()

        output += self.user_info()

        for class_name in self.schedule:
            output += self.schedule_cell(class_name)

        output += self.close_row()
        return output


@register.filter('schedule_table')
def schedule_table(schedule):
    table_node = ScheduleTableNode(schedule)
    return table_node.render()
