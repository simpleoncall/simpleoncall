from django.conf.urls import patterns, include, url

from simpleoncall.api import v1

urlpatterns = patterns(
    '',
    url(r'^$', 'simpleoncall.api.views.index', name='api-index'),
    url(r'^v1/', include(v1.urls.urlpatterns, namespace='api-v1')),
)
