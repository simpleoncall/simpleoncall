from django.contrib.auth import login as login_user, authenticate
from django.core.urlresolvers import reverse
from django.forms.utils import ErrorList
from django.http import JsonResponse
from django.template import RequestContext
from django.template.loader import render_to_string

from simpleoncall.decorators import parse_body
from simpleoncall.forms.auth import AuthenticationForm, RegistrationForm


class InternalResponse(JsonResponse):
    def __init__(self, redirect=None, error=None, html=None):
        super(InternalResponse, self).__init__({
            'redirect': redirect,
            'error': error,
            'html': html,
        })


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
