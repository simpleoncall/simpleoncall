__all__ = ['urls', 'InternalResponse']

from django.http import JsonResponse

from simpleoncall.internal import urls


class InternalResponse(JsonResponse):
    def __init__(self, redirect=None, error=None, html=None):
        super(InternalResponse, self).__init__({
            'redirect': redirect,
            'error': error,
            'html': html,
        })
