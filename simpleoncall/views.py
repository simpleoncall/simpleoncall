from functools import wraps

from django.contrib.auth import login as login_user, authenticate
from django.contrib.auth import logout as logout_user
from django.core.urlresolvers import reverse
from django.forms.utils import ErrorList
from django.http import HttpResponseRedirect
from django.shortcuts import render

from simpleoncall.forms.auth import AuthenticationForm, RegistrationForm


def require_authentication():
    def wrapped(func):
        @wraps(func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated():
                return HttpResponseRedirect(reverse('login'))
            return func(request, *args, **kwargs)
        return _wrapped
    return wrapped


@require_authentication()
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
def settings(request):
    return render(request, 'settings.html', {'title': 'Settings'})


@require_authentication()
def account(request):
    return render(request, 'account.html', {'title': 'Account'})


@require_authentication()
def alerts(request):
    return render(request, 'alerts.html', {'title': 'Alerts'})


@require_authentication()
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
