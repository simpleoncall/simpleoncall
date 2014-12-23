from django.conf.urls import patterns, include, url
from django.contrib import admin

from simpleoncall import api

urlpatterns = patterns(
    '',
    url(r'^$', 'simpleoncall.views.dashboard', name='dashboard'),
    url(r'^login', 'simpleoncall.views.login', name='login'),
    url(r'^logout', 'simpleoncall.views.logout', name='logout'),
    url(r'^settings', 'simpleoncall.views.settings', name='settings'),
    url(r'^account', 'simpleoncall.views.account', name='account'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(api.urlpatterns, namespace='api')),
)
