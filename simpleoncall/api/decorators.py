import base64
from functools import wraps

from simpleoncall.models import APIKey


def requires_authentication():
    def wrapped(func):
        @wraps(func)
        def _wrapped(request, *args, **kwargs):
            auth = request.META.get('HTTP_AUTHORIZATION')
            if not auth:
                pass

            _, auth = auth.split(' ')
            username, password = base64.b64decode(auth).split(':')

            api_key = APIKey.objects.get(username=username, password=password)
            if not api_key:
                pass

            setattr(request, 'api_key', api_key)

            return func(request, *args, **kwargs)
        return _wrapped
    return wrapped
