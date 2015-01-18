from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt

from simpleoncall.decorators import requires_api_key, parse_body
from simpleoncall.api import APIResponse
from simpleoncall.models import Alert, EventStatus


@requires_api_key()
def index(request):
    result = {
        'current_team': request.api_key.team.name,
        'users': [u.email for u in request.api_key.team.users.only('email')],
    }
    return APIResponse(result=result)


@requires_api_key()
def whose_oncall(request):
    schedule = request.api_key.team.get_active_schedule()
    oncall = None
    if schedule:
        oncall = schedule.get_currently_on_call()
        oncall = oncall.email

    return APIResponse(result=oncall)


@requires_api_key()
@csrf_exempt
@parse_body()
def alert_create(request):
    if not request.method == 'POST':
        return APIResponse(error='Invalid Request Method', status_code=405)

    if not isinstance(request.data, dict):
        return APIResponse(error='Invalid Request Data', status_code=400)

    title = request.data.get('title')
    if not title:
        return APIResponse(error='Must provide "title" property', status_code=400)

    alert = Alert(team=request.api_key.team, created_by_api_key=request.api_key, title=title)
    alert.body = request.data.get('body')
    alert.status = request.data.get('status', EventStatus.OPEN)
    if alert.status not in EventStatus.STATUSES:
        return APIResponse(error='Unknown Alert status %r' % (alert.status, ), status_code=400)

    try:
        alert.save(api_key=request.api_key)
    except IntegrityError:
        return APIResponse(error='Error while saving alert', status_code=400)

    return APIResponse(result={'id': alert.id}, status_code=202)
