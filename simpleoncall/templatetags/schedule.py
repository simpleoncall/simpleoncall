import calendar
import datetime

from django import template
from django.utils import timezone

from simpleoncall.templatetags.gravatar import gravatar_url

register = template.Library()


class ScheduleCalendarDayNode(template.Node):
    def __init__(self, schedule, day, now=None):
        self.schedule = schedule
        starting_time = schedule.starting_time if schedule else 0
        self.day = datetime.datetime(day.year, day.month, day.day, starting_time, tzinfo=timezone.utc)
        self.now = now or timezone.now()

    def render(self, context=None):
        oncall = None
        if self.schedule:
            oncall = self.schedule.get_currently_on_call(self.day)
        status = 'oncall' if oncall else ''
        output = '<div class="schedule-calendar-day pure-u-3-24 pure-g" data-day="%s">' % (self.day.day, )
        if self.now.month != self.day.month:
            output += '<div class="schedule-calendar-overlay"></div>'
        output += '<div class="schedule-calendar-date pure-u-1">%s</div>' % (self.day.day, )
        output += '<div class="schedule-calendar-data pure-u-1 %s">' % (status, )
        if oncall:
            output += '%s' % (gravatar_url(oncall.email), )
            output += '<span class="name">%s</span>' % (oncall.get_display_name(), )
        output += '</div>'
        output += '</div>'
        return output


class ScheduleCalendarWeekNode(template.Node):
    def __init__(self, schedule, week_data, week_num, now=None):
        self.schedule = schedule
        self.week_num = week_num
        self.week_data = week_data
        self.now = now or timezone.now()

    def render(self, context=None):
        output = '<div class="schedule-calendar-week pure-u-7-8 pure-g" data-week-id="%s">' % (self.week_num, )
        for day in self.week_data:
            output += ScheduleCalendarDayNode(self.schedule, day).render()
        output += '</div>'
        return output


class ScheduleCalendarNode(calendar.HTMLCalendar, template.Node):
    def __init__(self, schedule, now=None):
        self.schedule = schedule
        self.now = now or timezone.now()
        super(ScheduleCalendarNode, self).__init__()

    def render(self, context=None):
        month_calendar = self.monthdatescalendar(self.now.year, self.now.month)
        output = '<div class="schedule-calendar pure-u-1 pure-g" data-year="%s" data-month="%s">' % (
            self.now.year, self.now.month
        )
        for num, week in enumerate(month_calendar):
            output += ScheduleCalendarWeekNode(self.schedule, week, num, now=self.now).render()

        output += '</div>'
        return output


@register.filter('schedule_calendar')
def schedule_calendar(schedule):
    return ScheduleCalendarNode(schedule).render()
