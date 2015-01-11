__all__ = ['urls']

from django.http import JsonResponse

from simpleoncall.api import urls


class APIResponse(JsonResponse):
    def __init__(self, error=None, result=None, status_code=200):
        super(APIResponse, self).__init__({
            'status': 'error' if error is not None else 'success',
            'error': error,
            'result': result,
        }, status=status_code)
