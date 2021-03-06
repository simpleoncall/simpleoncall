import datetime
import json

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from simpleoncall.decorators import requires_api_key, parse_body
from simpleoncall.api import APIResponse
from simpleoncall.models import Alert, EventStatus, ServiceData, Services
from simpleoncall.tasks.notificatons import send_alert_notifications


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
    if not EventStatus.valid(alert.status):
        return APIResponse(error='Unknown Alert status %r' % (alert.status, ), status_code=400)

    try:
        alert.save(api_key=request.api_key)
    except IntegrityError:
        return APIResponse(error='Error while saving alert', status_code=400)

    schedule = request.api_key.team.get_active_schedule()
    if schedule:
        oncall = schedule.get_currently_on_call()
        send_alert_notifications(oncall, alert)

    return APIResponse(result={'id': alert.id}, status_code=201)


@requires_api_key()
@csrf_exempt
@parse_body()
def alert_update(request):
    if not request.method == 'POST':
        return APIResponse(error='Invalid Request Method', status_code=405)

    if not isinstance(request.data, dict):
        return APIResponse(error='Invalid Request Data', status_code=400)

    alert_id = request.data.get('id')
    if not alert_id:
        return APIResponse(error='Alert "id" property is required', status_code=400)

    alert = Alert.objects.get(id=alert_id)
    if not alert:
        return APIResponse(error='Alert with id %r not found' % (alert_id, ), status_code=404)

    status = request.data.get('status')
    if not EventStatus.valid(status):
        return APIResponse(error='Unknown Alert status %r' % (status, ), status_code=400)
    alert.status = status

    try:
        alert.save(api_key=request.api_key)
    except IntegrityError:
        return APIResponse(error='Error while saving alert %s' % (alert.id, ), status_code=400)

    return APIResponse(result=alert.to_dict(), status_code=200)


@requires_api_key()
def alerts_list(request):
    query = ~Q(status=EventStatus.RESOLVED)
    if request.GET.get('status'):
        query = Q(status=request.GET.get('status'))

    start_date = request.GET.get('start', timezone.now() - datetime.timedelta(days=1))
    end_date = request.GET.get('end', timezone.now() + datetime.timedelta(days=1))
    query = query & Q(date_updated__range=(start_date, end_date))

    if request.GET.get('id'):
        query = Q(id=request.GET.get('id'))

    try:
        alerts = Alert.objects.filter(query)
    except ValidationError:
        return APIResponse(error='Invalid request format', status_code=400)

    results = [a.to_dict() for a in alerts]

    return APIResponse(result=results, status_code=200)


@requires_api_key()
@csrf_exempt
@parse_body()
def datadog_integration(request):
    data = request.data or {}

    # dont pay attention to any event type other than 'metric_alert_monitor'
    if data.get('event_type') != 'metric_alert_monitor':
        return APIResponse(result={})

    aggregate_key = data.get('aggreg_key')

    if not aggregate_key:
        return APIResponse(error='Message must contain "aggreg_key"', status_code=400)

    # try to look up existing service data for this specific event
    service_data = None
    try:
        service_data = ServiceData.objects.get(service=Services.DATADOG, service_id=aggregate_key)
    except ObjectDoesNotExist:
        pass

    # if we have service data, then we should have an alert attached to it, try to find it
    alert = None
    if service_data is not None:
        try:
            alert = Alert.objects.get(service_data=service_data, team=request.api_key.team)
        except ObjectDoesNotExist:
            pass
    else:
        service_data = ServiceData(service=Services.DATADOG, service_id=aggregate_key)

    # an existing alert was not found, create a new one
    if alert is None:
        alert = Alert(service_data=service_data, team=request.api_key.team, created_by_api_key=request.api_key)

    title = data.get('event_title')
    body = data.get('event_msg')
    metric = data.get('event_metric')
    transition = data.get('alert_transition')

    if not title:
        title = 'Datadog event'
        if metric:
            title += ' for metric %s' % (metric, )
        if transition:
            title += ' %s' % (transition, )

    alert.title = title
    alert.body = body

    if transition == 'Triggered':
        alert.status = EventStatus.OPEN
    elif transition == 'Recovered':
        alert.status = EventStatus.RESOLVED

    service_data.data = json.dumps(data)
    try:
        alert.save(api_key=request.api_key)
        service_data.save(api_key=request.api_key)
    except IntegrityError:
        return APIResponse(error='Error while saving alert', status_code=400)

    # TODO: should probably send a notification for other statuses too
    if alert.status == EventStatus.OPEN:
        schedule = request.api_key.team.get_active_schedule()
        if schedule:
            oncall = schedule.get_currently_on_call()
            send_alert_notifications(oncall, alert)

    return APIResponse(result={'id': alert.id}, status_code=201)
