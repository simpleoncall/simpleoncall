from django.conf.urls import patterns, include, url
from django.contrib import admin

from simpleoncall import api

urlpatterns = patterns(
    '',
    url(r'^$', 'simpleoncall.views.index', name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(api.urlpatterns, namespace='api')),
)
