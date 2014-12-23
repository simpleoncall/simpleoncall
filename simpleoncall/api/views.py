from django.http import HttpResponse

import json


def json_response(context):
    return HttpResponse(json.dumps(context), content_type="application/json")


def index(request):
    return json_response({"hello": "world"})
