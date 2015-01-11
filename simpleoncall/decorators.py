from functools import wraps
import json

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from simpleoncall.models import TeamMember


def require_authentication(require_team=True):
    def wrapped(func):
        @wraps(func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated():
                return HttpResponseRedirect(reverse('login'))
            if require_team:
                teams = TeamMember.objects.filter(user=request.user)
                if not teams:
                    return HttpResponseRedirect(reverse('create-team'))
            return func(request, *args, **kwargs)
        return _wrapped
    return wrapped


def require_selected_team():
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
                else:
                    return HttpResponseRedirect(reverse('select-team'))

            team_id, team_name = request.session['team'].values()
            teams = TeamMember.objects.filter(user=request.user, team_id=team_id)
            if not teams:
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
