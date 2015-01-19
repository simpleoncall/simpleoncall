import contextlib
import datetime
import json
import StringIO

from django.contrib.auth import logout as logout_user
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponse, HttpResponseBadRequest
from django.db.models import Count
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.http import urlencode, urlquote

from django_ical import feedgenerator

from simpleoncall.forms.auth import AuthenticationForm, RegistrationForm
from simpleoncall.forms.account import EditAccountForm, ChangePasswordForm
from simpleoncall.forms.schedule import TeamScheduleForm
from simpleoncall.forms.team import CreateTeamForm, SelectTeamForm, InviteTeamForm
from simpleoncall.decorators import require_authentication, require_selected_team
from simpleoncall.models import APIKey, TeamMember, TeamInvite, User, TeamSchedule
from simpleoncall.models import Alert, EventStatus, AlertSetting, AlertType


@require_authentication()
@require_selected_team()
def dashboard(request):
    end = timezone.now()
    start = end - datetime.timedelta(hours=12)
    date_added__range = (start, end)

    alerts = Alert.objects.filter(team=request.team, date_added__range=date_added__range).order_by('-date_added')[:10]
    alert_statuses = Alert.objects.filter(
        team=request.team, date_added__range=date_added__range
    ).values('status').annotate(total=Count('status'))

    alert_times = Alert.objects.filter(
        team=request.team, date_added__range=date_added__range
    ).values('date_added').annotate(total=Count('date_added')).order_by('-date_added')

    alert_timeseries = {}
    while start <= end:
        bucket = start - datetime.timedelta(minutes=start.minute % 60,
                                            seconds=start.second,
                                            microseconds=start.microsecond)
        alert_timeseries[bucket.strftime('%s')] = 0
        start += datetime.timedelta(minutes=60)

    for alert in alert_times:
        added = alert['date_added']
        bucket = added - datetime.timedelta(minutes=added.minute % 60,
                                            seconds=added.second,
                                            microseconds=added.microsecond)
        alert_timeseries[bucket.strftime('%s')] += alert['total']

    context = {
        'title': 'Dashboard',
        'alerts': alerts,
        'statuses': dict((a['status'], a['total']) for a in alert_statuses),
        'timeseries': json.dumps(alert_timeseries),
    }
    return render(request, 'dashboard.html', context)


def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('dashboard'))

    context = {
        'login_form': AuthenticationForm(),
        'register_form': RegistrationForm(),
        'login': True,
        'title': 'Login',
    }
    return render(request, 'login.html', context)


def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('dashboard'))

    context = {
        'login_form': AuthenticationForm(),
        'register_form': RegistrationForm(),
        'register': True,
        'title': 'Register',
        'next': urlquote(request.GET.get('next')),
    }
    return render(request, 'login.html', context)


def logout(request):
    logout_user(request)
    return HttpResponseRedirect(reverse('login'))


@require_authentication()
@require_selected_team()
def settings(request):
    api_keys = APIKey.objects.filter(team=request.team)
    members = TeamMember.objects.filter(team=request.team)

    context = {
        'title': '%s Settings' % (request.team.name, ),
        'api_keys': api_keys,
        'members': members,
        'invite_team_form': InviteTeamForm(),
    }
    return render(request, 'settings.html', context)


@require_authentication()
def account(request):
    alerts = request.user.get_alert_settings()
    if not alerts:
        alerts = [
            AlertSetting(id=0, type=AlertType.EMAIL, time=0)
        ]

    context = {
        'title': 'Account',
        'edit_account_form': EditAccountForm(instance=request.user),
        'change_password_form': ChangePasswordForm(instance=request.user),
        'alerts': alerts,
    }
    return render(request, 'account.html', context)


@require_authentication()
@require_selected_team()
def alerts(request):
    alert_count = Alert.objects.filter(team=request.team).count()
    alerts = Alert.objects.filter(team=request.team).order_by('-date_updated')[:10]
    context = {
        'title': 'Alerts',
        'alert_count': alert_count,
        'alerts': alerts,
    }
    return render(request, 'alerts.html', context)


@require_authentication()
@require_selected_team()
def schedule(request):
    schedule = request.team.get_active_schedule()
    oncall = None
    if schedule:
        oncall = schedule.get_currently_on_call()
    context = {
        'title': 'Schedule',
        'schedule': schedule,
        'oncall': oncall,
    }
    return render(request, 'schedule.html', context)


@require_authentication(require_team=False)
def create_team(request):
    create_team_form = CreateTeamForm(request.POST or None)
    if create_team_form.is_valid():
        team = create_team_form.save(request)
        messages.success(request, 'New team %s created' % team.name)
        return HttpResponseRedirect(reverse('dashboard'))

    context = {
        'title': 'Create New Team',
        'create_team_form': create_team_form,
    }
    return render(request, 'team/create.html', context)


@require_authentication()
def select_team(request):
    select_team_form = SelectTeamForm(request.POST or None, request.user)
    if select_team_form.is_valid():
        team = select_team_form.save(request)
        messages.success(request, 'Team changed to %s' % team.name)
        return HttpResponseRedirect(reverse('dashboard'))

    context = {
        'title': 'Select Team',
        'select_team_form': select_team_form,
    }
    return render(request, 'team/select.html', context)


def invite_accept(request):
    code = request.GET.get('code')
    email = request.GET.get('email')
    if not code or not email:
        return HttpResponseRedirect(reverse('dashboard'))

    invite = TeamInvite.objects.get(invite_code=code, email=email)
    if not invite:
        return HttpResponseRedirect(reverse('dashboard'))

    user = User.objects.get(email=email)
    if user:
        try:
            team_member = TeamMember.objects.get(team=invite.team, user=user)
        except ObjectDoesNotExist:
            team_member = None
        if team_member:
            messages.warning(request, 'already a member of team %s' % (invite.team.name, ))
        else:
            team_member = TeamMember(team=invite.team, user=user)
            team_member.save()
            messages.success(request, 'added to team %s' % (invite.team.name, ))
    else:
        args = {
            'code': code,
            'email': email,
        }
        next = '%s?%s' % (reverse('invite-accept'), urlencode(args))
        redirect = '%s?next=%s' % (reverse('register'), urlquote(next))
        return HttpResponseRedirect(redirect)

    return HttpResponseRedirect(reverse('dashboard'))


@require_authentication()
@require_selected_team()
def alert_ack(request, alert_id):
    alert = Alert.objects.get(id=alert_id)
    if not alert:
        messages.error(request, 'Alert %s was not found' % (alert_id, ))
    elif alert.status == EventStatus.ACKNOWLEDGED:
        messages.warning(request, 'Alert %s already acknowledged' % (alert_id, ))
    else:
        alert.status = EventStatus.ACKNOWLEDGED
        alert.save(user=request.user)
        messages.success(request, 'Alert %s was acknowledged' % (alert_id, ))

    return HttpResponseRedirect(reverse('alerts'))


@require_authentication()
@require_selected_team()
def alert_resolve(request, alert_id):
    alert = Alert.objects.get(id=alert_id, team=request.team)
    if not alert:
        messages.error(request, 'Alert %s was not found' % (alert_id, ))
    elif alert.status == EventStatus.RESOLVED:
        messages.warning(request, 'Alert %s already resolved' % (alert_id, ))
    else:
        alert.status = EventStatus.RESOLVED
        alert.save(user=request.user)
        messages.success(request, 'Alert %s was resolved' % (alert_id, ))

    return HttpResponseRedirect(reverse('alerts'))


@require_authentication()
@require_selected_team()
def alert_view(request, alert_id):
    alert = Alert.objects.get(id=alert_id, team=request.team)
    if not alert:
        messages.error(request, 'Alert %s was not found' % (alert_id, ))
        return HttpResponseRedirect(reverse('dashboard'))

    context = {
        'title': alert.title,
        'event': alert,
    }
    return render(request, 'alert.html', context)


@require_authentication()
@require_selected_team()
def edit_schedule(request):
    msg = None
    schedule_id = None
    if 'schedule_id' in request.POST:
        schedule_id = int(request.POST['schedule_id'])

    dummy_schedule = TeamSchedule(team=request.team)
    data = None if schedule_id else request.POST or None
    new_schedule_form = TeamScheduleForm(request.team, data, instance=dummy_schedule)
    saved = False
    if request.method == 'POST' and not schedule_id:
        if new_schedule_form.is_valid():
            new_schedule_form.save()
            saved = True
            msg = 'New Schedule Added'

    schedule_forms = []
    for schedule in request.team.get_schedules():
        data = None
        if schedule.id == schedule_id:
            data = request.POST
        schedule_form = TeamScheduleForm(request.team, data, instance=schedule)
        if data and schedule_form.is_valid():
            schedule_form.save()
            msg = 'Schedule Updated'
        schedule_forms.append(schedule_form)

    if msg:
        messages.success(request, msg)

    context = {
        'title': 'Edit Schedule',
        'active_schedule': request.team.get_active_schedule(),
        'schedule_forms': schedule_forms,
        'new_schedule_form': new_schedule_form,
        'hidden_schedule_form': not saved or request.method != 'POST',
    }
    return render(request, 'edit_schedule.html', context)


@require_authentication()
@require_selected_team()
def delete_schedule(request):
    id = request.GET.get('id')
    if id:
        schedule = TeamSchedule.objects.get(team=request.team, id=id)
        schedule.delete()
        messages.success(request, 'Schedule %s Deleted' % (schedule.name, ))
    else:
        messages.error(request, 'Unknown Schedule Id')
    return HttpResponseRedirect(reverse('edit-schedule'))


@require_authentication()
@require_selected_team()
def partial(request, partial):
    context = {
        'request': request,
        'user': request.user,
        'team': request.team,
    }
    html = render_to_string('partials/%s.html' % (partial, ), context)
    return JsonResponse({'html': html})


@require_authentication()
@require_selected_team()
def team_calendar(request):
    schedule = request.team.get_active_schedule()
    if not schedule:
        return Http404('Unkown Calendar')

    feed = feedgenerator.ICal20Feed(
        title='Team %s On-Call Schedule %s' % (request.team.name, schedule.name),
        link=request.build_absolute_uri(request.path),
        description='Team %s On-Call Schedule %s' % (request.team.name, schedule.name),
        language='en',
        subtitle='Generated by SimpleOnCall',
        author_email='service@simpleoncall.com',
        author_link='http://simpleoncall.com',
        author_name='SimpleOnCall',
        feed_url=request.build_absolute_uri(request.path)
    )
    now = timezone.now()
    starting_time = datetime.datetime(now.year, now.month, now.day, schedule.starting_time, tzinfo=timezone.utc)
    next_start_time = None
    currently_oncall = None
    for i in xrange(90):
        now = starting_time + datetime.timedelta(days=i)
        oncall = schedule.get_currently_on_call(now)
        if next_start_time is None:
            next_start_time = now
            currently_oncall = oncall
        elif currently_oncall.id != oncall.id:
            feed.add_item(
                title='%s On-Call' % (oncall.get_display_name(), ),
                link=request.build_absolute_uri(reverse('schedule')),
                description='%s On-Call' % (currently_oncall.get_display_name(), ),
                start_datetime=next_start_time,
                end_datetime=now
            )
            next_start_time = now
            currently_oncall = oncall

    feed.add_item(
        title='%s On-Call' % (oncall.get_display_name(), ),
        link=request.build_absolute_uri(reverse('schedule')),
        description='%s On-Call' % (currently_oncall.get_display_name(), ),
        start_datetime=next_start_time,
        end_datetime=now
    )

    results = None
    with contextlib.closing(StringIO.StringIO()) as output:
        feed.write(output, 'utf-8')
        results = output.getvalue()
    if results is not None:
        return HttpResponse(results, content_type='text/calendar; charset=utf-8')
    return HttpResponseBadRequest('Could not generate iCal at this time')
