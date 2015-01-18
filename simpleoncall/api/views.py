import json
import random

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from simpleoncall.decorators import requires_api_key
from simpleoncall.models import TeamMember, Alert, EventStatus


def json_response(context, status_code=200):
    return HttpResponse(json.dumps(context), status=status_code, content_type="application/json")


def json_error(error_message, status_code=400):
    return json_response({
        'result': None,
        'error': error_message
    }, status_code=status_code)


@requires_api_key()
def index(request):
    return json_response({'team': request.api_key.team.name})


@requires_api_key()
def v1_get_oncall(request):
    team_members = TeamMember.objects.filter(team=request.api_key.team)
    oncall_member = random.choice(team_members)
    user = oncall_member.user
    return json_response({
        'oncall': {
            'name': user.get_full_name(),
            'email': user.email,
        }
    })


@requires_api_key()
@csrf_exempt
def v1_alert_create(request):
    if not request.method == 'POST':
        return json_error('Invalid Request Method', status_code=405)

    data = json.loads(request.body)
    alert = Alert(
        team=request.api_key.team,
        created_by_api_key=request.api_key
    )
    for key, value in data.iteritems():
        if hasattr(alert, key):
            setattr(alert, key, value)

    alert.save(api_key=request.api_key)
    return json_response({
        'result': alert.id,
    })


@requires_api_key()
@csrf_exempt
def v1_alerts_status(request, status=EventStatus.OPEN):
    alerts = Alert.objects.filter(status=status, team=request.api_key.team)

    results = {
        'results': [alert.to_dict() for alert in alerts],
    }
    return json_response(results)
