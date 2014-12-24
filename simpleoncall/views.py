from django.contrib.auth import login as login_user, authenticate
from django.contrib.auth import logout as logout_user
from django.core.urlresolvers import reverse
from django.forms.utils import ErrorList
from django.http import HttpResponseRedirect
from django.shortcuts import render

from simpleoncall.forms.auth import AuthenticationForm, RegistrationForm
from simpleoncall.forms.account import EditAccountForm, ChangePasswordForm
from simpleoncall.forms.team import CreateTeamForm, SelectTeamForm
from simpleoncall.decorators import require_authentication, require_selected_team


@require_authentication()
@require_selected_team()
def dashboard(request):
    return render(request, 'dashboard.html', {'title': 'Dashboard'})


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
        return HttpResponseRedirect(reverse('dashboard'))

    context = {
        'login_form': AuthenticationForm(),
        'register_form': register_form,
        'register': True,
        'title': 'Register',
    }
    return render(request, 'auth/login.html', context)


def logout(request):
    logout_user(request)
    return HttpResponseRedirect(reverse('login'))


@require_authentication()
@require_selected_team()
def settings(request):
    return render(request, 'settings.html', {'title': 'Settings'})


@require_authentication()
def account(request):
    password_form = request.POST and request.POST.get('password_form') is not None
    change_password_form_data = request.POST if password_form else None
    edit_account_form_data = request.POST if not password_form else None

    edit_account_form = EditAccountForm(edit_account_form_data or None, instance=request.user)
    change_password_form = ChangePasswordForm(change_password_form_data or None, instance=request.user)

    if edit_account_form.is_valid():
        edit_account_form.save()
    elif change_password_form.is_valid():
        if change_password_form.cleaned_data['password_1'] == change_password_form.cleaned_data['password_2']:
            from django.conf import settings
            user = change_password_form.save()
            user.backend = settings.AUTHENTICATION_BACKENDS[0]
            login_user(request, user)
        else:
            errors = change_password_form._errors.setdefault('password_1', ErrorList())
            errors.append('Passwords do not match')

    context = {
        'title': 'Account',
        'edit_account_form': edit_account_form,
        'change_password_form': change_password_form,
    }
    return render(request, 'account.html', context)


@require_authentication()
@require_selected_team()
def alerts(request):
    return render(request, 'alerts.html', {'title': 'Alerts'})


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
        'users': [
            {
                'user': request.user,
                'schedule': [
                    'oncall',
                    'oncall',
                    'standby',
                    'free',
                    'free',
                    'oncall',
                    'standby',
                ]
            }
        ]
    }

    context = {
        'title': 'Schedule',
        'schedule': oncall_schedule,
    }
    return render(request, 'schedule.html', context)


@require_authentication(require_team=False)
def create_team(request):
    create_team_form = CreateTeamForm(request.POST or None)
    if create_team_form.is_valid():
        create_team_form.save(request.user)

    context = {
        'title': 'Create New Team',
        'create_team_form': create_team_form,
    }
    return render(request, 'team/create.html', context)


@require_authentication()
def select_team(request):
    select_team_form = SelectTeamForm(request.POST or None, request.user)
    if select_team_form.is_valid():
        select_team_form.save(request)
        return HttpResponseRedirect(reverse('dashboard'))

    context = {
        'title': 'Select Team',
        'select_team_form': select_team_form,
    }
    return render(request, 'team/select.html', context)
