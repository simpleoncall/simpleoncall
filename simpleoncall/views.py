from functools import wraps

from django.contrib.auth import logout as logout_user
from django.contrib.auth import login as login_user, authenticate

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from simpleoncall.forms.auth import AuthenticationForm


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
    return render(request, 'index.html', {'text': 'dashboard'})


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

    context = {
        'form': login_form,
    }
    return render(request, 'auth/login.html', context)


def logout(request):
    logout_user(request)
    return HttpResponseRedirect(reverse('login'))


@require_authentication()
def settings(request):
    return render(request, 'index.html', {'text': 'settings'})


@require_authentication()
def account(request):
    return render(request, 'index.html', {'text': 'account'})
