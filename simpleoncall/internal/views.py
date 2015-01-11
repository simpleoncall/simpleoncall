from django.contrib import messages
from django.contrib.auth import login as login_user, authenticate
from django.core.urlresolvers import reverse
from django.forms.utils import ErrorList
from django.template import RequestContext
from django.template.loader import render_to_string

from simpleoncall.decorators import parse_body, require_authentication
from simpleoncall.forms.account import ChangePasswordForm, EditAccountForm
from simpleoncall.forms.auth import AuthenticationForm, RegistrationForm
from simpleoncall.internal import InternalResponse


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
    return InternalResponse()
