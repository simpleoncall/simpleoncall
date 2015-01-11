from functools import wraps
import base64
import json

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from simpleoncall.api import APIResponse
from simpleoncall.models import TeamMember, APIKey
from simpleoncall.internal import InternalResponse


def require_authentication(require_team=True, internal=False):
    def wrapped(func):
        @wraps(func)
        def _wrapped(request, *args, **kwargs):
            redirect = None
            if not request.user.is_authenticated():
                redirect = reverse('login')
            elif require_team:
                teams = TeamMember.objects.filter(user=request.user)
                if not teams:
                    redirect = reverse('create-team')

            if redirect:
                if internal:
                    return InternalResponse(redirect=redirect)
                return HttpResponseRedirect(redirect)

            return func(request, *args, **kwargs)
        return _wrapped
    return wrapped


def require_selected_team(internal=False):
    def wrapped(func):
        @wraps(func)
        def _wrapped(request, *args, **kwargs):
            if not request.session.get('team'):
                teams = TeamMember.objects.filter(user=request.user)
                if teams:
                    request.session['team'] = {
                        'id': teams[0].team.id,
                        'name': teams[0].team.name,
                    }
                elif internal:
                    return InternalResponse(redirect=reverse('select-team'))
                else:
                    return HttpResponseRedirect(reverse('select-team'))

            team_id, team_name = request.session['team'].values()
            teams = TeamMember.objects.filter(user=request.user, team_id=team_id)
            if not teams:
                if internal:
                    return InternalResponse(redirect=reverse('select-team'))
                else:
                    return HttpResponseRedirect(reverse('select-team'))

            setattr(request, 'team', teams[0].team)

            return func(request, *args, **kwargs)
        return _wrapped
    return wrapped


def parse_body():
    def wrapped(func):
        @wraps(func)
        def _wrapped(request, *args, **kwargs):
            data = None
            if request.method == 'POST':
                data = request.read()
                if data:
                    data = json.loads(data)

            request.data = data
            return func(request, *args, **kwargs)
        return _wrapped
    return wrapped


def requires_api_key():
    def wrapped(func):
        @wraps(func)
        def _wrapped(request, *args, **kwargs):
            auth = request.META.get('HTTP_AUTHORIZATION')
            if not auth:
                return APIResponse(error='Not Authorized', status_code=401)

            _, auth = auth.split(' ')
            username, password = base64.b64decode(auth).split(':')

            api_key = APIKey.objects.get(username=username, password=password)
            if not api_key:
                pass

            setattr(request, 'api_key', api_key)

            return func(request, *args, **kwargs)
        return _wrapped
    return wrapped
