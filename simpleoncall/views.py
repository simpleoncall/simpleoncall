import datetime
import json
import random

from django.contrib.auth import login as login_user, authenticate
from django.contrib.auth import logout as logout_user
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms.utils import ErrorList
from django.http import HttpResponseRedirect, HttpResponse
from django.db import IntegrityError
from django.db.models import Q, Count
from django.shortcuts import render
from django.utils import timezone
from django.utils.http import urlencode, urlquote

from simpleoncall.forms.auth import AuthenticationForm, RegistrationForm
from simpleoncall.forms.account import EditAccountForm, ChangePasswordForm
from simpleoncall.forms.team import CreateTeamForm, SelectTeamForm, InviteTeamForm
from simpleoncall.decorators import require_authentication, require_selected_team
from simpleoncall.models import APIKey, TeamMember, TeamInvite, User
from simpleoncall.models import Event, EventType, EventStatus, AlertSetting, AlertType


@require_authentication()
@require_selected_team()
def dashboard(request):
    end = timezone.now()
    start = end - datetime.timedelta(hours=12)
    date_added__range = (start, end)

    query = Q(team=request.team) | Q(user=request.user)
    events = Event.objects.filter(query, date_added__range=date_added__range).order_by('-date_added')[:10]

    event_statuses = Event.objects.filter(
        team=request.team, type=EventType.ALERT,
        date_added__range=date_added__range
    ).values('status').annotate(total=Count('status'))

    event_times = Event.objects.filter(
        team=request.team, type=EventType.ALERT,
        date_added__range=date_added__range
    ).values('date_added').annotate(total=Count('date_added')).order_by('-date_added')

    event_timeseries = {}
    while start <= end:
        bucket = start - datetime.timedelta(minutes=start.minute % 60,
                                            seconds=start.second,
                                            microseconds=start.microsecond)
        event_timeseries[bucket.strftime('%s')] = 0
        start += datetime.timedelta(minutes=60)

    for event in event_times:
        added = event['date_added']
        bucket = added - datetime.timedelta(minutes=added.minute % 60,
                                            seconds=added.second,
                                            microseconds=added.microsecond)
        event_timeseries[bucket.strftime('%s')] += event['total']

    context = {
        'title': 'Dashboard',
        'events': events,
        'statuses': dict((e['status'], e['total']) for e in event_statuses),
        'timeseries': json.dumps(event_timeseries),
    }
    return render(request, 'dashboard.html', context)


def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('dashboard'))

    login_form = AuthenticationForm(request.POST or None)
    if login_form.is_valid():
        user_cache = authenticate(
            username=login_form.cleaned_data['username'],
            password=login_form.cleaned_data['password']
        )
        if user_cache:
            login_user(request, user_cache)
            return HttpResponseRedirect(reverse('dashboard'))
        else:
            errors = login_form._errors.setdefault('username', ErrorList())
            errors.append('Incorrect Username or Password')

    context = {
        'login_form': login_form,
        'register_form': RegistrationForm(),
        'login': True,
        'title': 'Login',
    }
    return render(request, 'auth/login.html', context)


def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('dashboard'))

    register_form = RegistrationForm(request.POST or None)
    if register_form.is_valid():
        from django.conf import settings
        user = register_form.save()
        user.backend = settings.AUTHENTICATION_BACKENDS[0]
        login_user(request, user)

        redirect = reverse('dashboard')
        if request.GET.get('next'):
            redirect = request.GET.get('next')
        return HttpResponseRedirect(redirect)

    context = {
        'login_form': AuthenticationForm(),
        'register_form': register_form,
        'register': True,
        'title': 'Register',
        'next': urlquote(request.GET.get('next')),
    }
    return render(request, 'auth/login.html', context)


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
    }
    return render(request, 'settings.html', context)


@require_authentication()
@require_selected_team()
def create_key(request):
    api_key = APIKey(
        team=request.team,
        created_by=request.user,
    )
    api_key.save()
    event = Event(
        title='API key %s created' % (api_key.get_name(), ),
        type=EventType.AUDIT,
        status=EventStatus.RESOLVED,
        team=request.team,
        created_by_user=request.user,
    )
    event.save(user=request.user)
    messages.success(request, event.title)
    return HttpResponseRedirect(reverse('settings'))


@require_authentication()
def account(request):
    password_form = request.POST and request.POST.get('password_form') is not None
    change_password_form_data = request.POST if password_form else None
    edit_account_form_data = request.POST if not password_form else None

    edit_account_form = EditAccountForm(edit_account_form_data or None, instance=request.user)
    change_password_form = ChangePasswordForm(change_password_form_data or None, instance=request.user)

    if edit_account_form.is_valid():
        edit_account_form.save()
        messages.success(request, 'Account info saved')
    elif change_password_form.is_valid():
        if change_password_form.cleaned_data['password_1'] == change_password_form.cleaned_data['password_2']:
            from django.conf import settings
            user = change_password_form.save()
            user.backend = settings.AUTHENTICATION_BACKENDS[0]
            login_user(request, user)
            messages.success(request, 'Password successfully changed')
        else:
            errors = change_password_form._errors.setdefault('password_1', ErrorList())
            errors.append('Passwords do not match')

    alerts = request.user.get_alert_settings()
    if not alerts:
        alerts = [
            AlertSetting(id=0, type=AlertType.EMAIL, time=0)
        ]

    context = {
        'title': 'Account',
        'edit_account_form': edit_account_form,
        'change_password_form': change_password_form,
        'alerts': alerts,
    }
    return render(request, 'account.html', context)


@require_authentication()
@require_selected_team()
def save_alert_settings(request):
    settings = json.loads(request.read())
    success = True

    for setting in settings:
        alert = None
        if setting['id']:
            alert = AlertSetting.objects.get(id=setting['id'], user=request.user)

        if not alert:
            alert = AlertSetting(user=request.user)

        changed = not setting['id'] or alert.type != setting['type'] or alert.time != setting['time']
        if changed:
            alert.type = setting['type']
            alert.time = setting['time']
            try:
                alert.save()
            except IntegrityError:
                success = False

    response_data = {
        'success': success,
    }
    return HttpResponse(json.dumps(response_data), content_type='application/json')


@require_authentication()
@require_selected_team()
def alerts(request):
    alert_count = Event.objects.filter(team=request.team, type=EventType.ALERT).count()
    alerts = Event.objects.filter(team=request.team, type=EventType.ALERT).order_by('-date_updated')[:10]
    context = {
        'title': 'Alerts',
        'alert_count': alert_count,
        'alerts': alerts,
    }
    return render(request, 'alerts.html', context)


@require_authentication()
@require_selected_team()
def schedule(request):
    oncall_schedule = {
        'labels': [
            {
                'short_name': 'Mon',
                'long_name': 'Monday',
            },
            {
                'short_name': 'Tue',
                'long_name': 'Tuesday',
            },
            {
                'short_name': 'Wed',
                'long_name': 'Wednesday',
            },
            {
                'short_name': 'Thu',
                'long_name': 'Thursday',
            },
            {
                'short_name': 'Fri',
                'long_name': 'Friday',
            },
            {
                'short_name': 'Sat',
                'long_name': 'Saturday',
            },
            {
                'short_name': 'Sun',
                'long_name': 'Sunday',
            }
        ],
        'users': []
    }

    users = TeamMember.objects.filter(team=request.team)
    for user in users:
        data = {'user': user.user, 'schedule': []}
        for _ in oncall_schedule['labels']:
            status = random.randint(1, 3)
            if status == 1:
                status = 'oncall'
            elif status == 2:
                status = 'standby'
            else:
                status = 'free'
            data['schedule'].append(status)
        oncall_schedule['users'].append(data)

    context = {
        'title': 'Schedule',
        'schedule': oncall_schedule,
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


@require_authentication()
@require_selected_team()
def invite_team(request):
    invite_team_form = InviteTeamForm(request.POST or None)
    if invite_team_form.is_valid():
        sent, existing, failed = invite_team_form.save(request)
        if sent:
            messages.success(request, '%s invites sent' % (sent, ))
        if existing:
            messages.warning(request, '%s users already added' % (existing, ))
        if failed:
            messages.error(request, '%s invites failed to send' % (failed, ))
        return HttpResponseRedirect(reverse('settings'))
    context = {
        'title': 'Invite Members',
        'invite_team_form': invite_team_form,
    }
    return render(request, 'team/invite.html', context)


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
        team_member = TeamMember.objects.get(team=invite.team, user=user)
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
def event_ack(request, event_id):
    event = Event.objects.get(id=event_id)
    if not event:
        messages.error(request, 'Event %s was not found' % (event_id, ))
    elif event.status == EventStatus.ACKNOWLEDGED:
        messages.warning(request, 'Event %s already acknowledged' % (event_id, ))
    else:
        event.status = EventStatus.ACKNOWLEDGED
        event.save(user=request.user)
        messages.success(request, 'Event %s was acknowledged' % (event_id, ))

    return HttpResponseRedirect(reverse('alerts'))


@require_authentication()
@require_selected_team()
def event_resolve(request, event_id):
    event = Event.objects.get(id=event_id, team=request.team)
    if not event:
        messages.error(request, 'Event %s was not found' % (event_id, ))
    elif event.status == EventStatus.RESOLVED:
        messages.warning(request, 'Event %s already resolved' % (event_id, ))
    else:
        event.status = EventStatus.RESOLVED
        event.save(user=request.user)
        messages.success(request, 'Event %s was resolved' % (event_id, ))

    return HttpResponseRedirect(reverse('alerts'))


@require_authentication()
@require_selected_team()
def event_view(request, event_id):
    event = Event.objects.get(id=event_id, team=request.team)
    if not event:
        messages.error(request, 'Event %s was not found' % (event_id, ))
        return HttpResponseRedirect(reverse('dashboard'))

    context = {
        'title': event.title,
        'event': event,
    }
    return render(request, 'event.html', context)


@require_authentication()
@require_selected_team()
def edit_schedule(request):
    context = {
        'title': 'Edit Schedule',
    }
    return render(request, 'edit_schedule.html', context)
