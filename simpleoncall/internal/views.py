from django.contrib import messages
from django.contrib.auth import login as login_user, authenticate
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.forms.utils import ErrorList
from django.template import RequestContext
from django.template.loader import render_to_string

from simpleoncall.decorators import parse_body, require_authentication, require_selected_team
from simpleoncall.forms.account import ChangePasswordForm, EditAccountForm
from simpleoncall.forms.auth import AuthenticationForm, RegistrationForm
from simpleoncall.forms.team import InviteTeamForm
from simpleoncall.internal import InternalResponse
from simpleoncall.models import AlertSetting, AlertType


@parse_body()
def login(request):
    if request.user.is_authenticated():
        return InternalResponse(redirect=reverse('dashboard'))

    login_form = AuthenticationForm(request.data)
    if login_form.is_valid():
        user_cache = authenticate(
            username=login_form.cleaned_data['username'],
            password=login_form.cleaned_data['password']
        )
        if user_cache:
            login_user(request, user_cache)
            return InternalResponse(redirect=reverse('dashboard'))
        else:
            errors = login_form._errors.setdefault('username', ErrorList())
            errors.append('Incorrect Username or Password')

    context = RequestContext(request, {
        'login_form': login_form,
    })
    html = render_to_string('auth/login-form.html', context)
    return InternalResponse(html=html)


@parse_body()
def register(request):
    if request.user.is_authenticated():
        return InternalResponse(redirect=reverse('dashboard'))

    register_form = RegistrationForm(request.data)
    if register_form.is_valid():
        from django.conf import settings
        user = register_form.save()
        user.backend = settings.AUTHENTICATION_BACKENDS[0]
        login_user(request, user)

        redirect = reverse('dashboard')
        if request.GET.get('next'):
            redirect = request.GET.get('next')
        return InternalResponse(redirect=redirect)

    context = RequestContext(request, {
        'register_form': register_form,
    })
    html = render_to_string('auth/register-form.html', context)
    return InternalResponse(html=html)


@require_authentication(internal=True)
@parse_body()
def account_info(request):
    edit_account_form = EditAccountForm(request.data, instance=request.user)
    if edit_account_form.is_valid():
        edit_account_form.save()
        messages.success(request, 'Account info saved')

    context = RequestContext(request, {
        'edit_account_form': edit_account_form,
    })
    html = render_to_string('partials/account/account-info.html', context)
    return InternalResponse(html=html)


@require_authentication(internal=True)
@parse_body()
def account_password(request):
    change_password_form = ChangePasswordForm(request.data, instance=request.user)
    if change_password_form.is_valid():
        if change_password_form.cleaned_data['password_1'] == change_password_form.cleaned_data['password_2']:
            from django.conf import settings
            user = change_password_form.save()
            user.backend = settings.AUTHENTICATION_BACKENDS[0]
            login_user(request, user)
            messages.success(request, 'Password Changed Successfully')
        else:
            errors = change_password_form._errors.setdefault('password_1', ErrorList())
            errors.append('Passwords do not match')

    context = RequestContext(request, {
        'change_password_form': change_password_form,
    })
    html = render_to_string('partials/account/change-password.html', context)
    return InternalResponse(html=html)


@require_authentication(internal=True)
@parse_body()
def account_alerts(request):
    data = request.data or {}
    settings = data.get('settings', [])

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
                messages.error(request, 'There was an error saving alert %s:%s' % (alert.type, alert.time))

    if success:
        messages.success(request, 'Alerts where saved successfully')

    alerts = request.user.get_alert_settings()
    if not alerts:
        alerts = [
            AlertSetting(id=0, type=AlertType.EMAIL, time=0)
        ]

    context = RequestContext(request, {
        'alerts': alerts,
    })
    html = render_to_string('partials/account/alert-schedule.html', context)
    return InternalResponse(html=html)


@require_authentication(internal=True)
@require_selected_team(internal=True)
@parse_body()
def team_invite(request):
    invite_team_form = InviteTeamForm(request.data)
    if invite_team_form.is_valid():
        sent, existing, failed = invite_team_form.save(request)
        if sent:
            messages.success(request, '%s invites sent' % (sent, ))
        if existing:
            messages.warning(request, '%s users already added' % (existing, ))
        if failed:
            messages.error(request, '%s invites failed to send' % (failed, ))
        if sent and not existing and not failed:
            invite_team_form = InviteTeamForm()

    context = RequestContext(request, {
        'invite_team_form': invite_team_form,
    })
    html = render_to_string('partials/team/invite.html', context)
    return InternalResponse(html=html)
