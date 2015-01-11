from simpleoncall.decorators import requires_api_key
from simpleoncall.api import APIResponse


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
