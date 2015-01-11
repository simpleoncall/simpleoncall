import datetime
import json

from django.contrib.auth import logout as logout_user
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.forms.utils import ErrorList
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.db import IntegrityError
from django.db.models import Q, Count
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.http import urlencode, urlquote

from simpleoncall.forms.auth import AuthenticationForm, RegistrationForm
from simpleoncall.forms.account import EditAccountForm, ChangePasswordForm
from simpleoncall.forms.schedule import TeamScheduleForm
from simpleoncall.forms.team import CreateTeamForm, SelectTeamForm, InviteTeamForm
from simpleoncall.decorators import require_authentication, require_selected_team
from simpleoncall.models import APIKey, TeamMember, TeamInvite, User, TeamSchedule
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

    context = {
        'login_form': AuthenticationForm(),
        'register_form': RegistrationForm(),
        'login': True,
        'title': 'Login',
    }
    return render(request, 'auth/login.html', context)


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
