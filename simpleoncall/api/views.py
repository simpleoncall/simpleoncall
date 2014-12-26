import json

from django.http import HttpResponse

from simpleoncall.api.decorators import requires_authentication


def json_response(context):
    return HttpResponse(json.dumps(context), content_type="application/json")


@requires_authentication()
def index(request):
    return json_response({'team': request.api_key.team.name})
