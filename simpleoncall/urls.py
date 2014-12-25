from django.conf.urls import patterns, include, url
from django.contrib import admin

from simpleoncall import api

urlpatterns = patterns(
    '',
    url(r'^$', 'simpleoncall.views.dashboard', name='dashboard'),
    url(r'^login', 'simpleoncall.views.login', name='login'),
    url(r'^register', 'simpleoncall.views.register', name='register'),
    url(r'^logout', 'simpleoncall.views.logout', name='logout'),
    url(r'^settings', 'simpleoncall.views.settings', name='settings'),
    url(r'^account', 'simpleoncall.views.account', name='account'),
    url(r'^schedule', 'simpleoncall.views.schedule', name='schedule'),
    url(r'^alerts', 'simpleoncall.views.alerts', name='alerts'),
    url(r'^team/create', 'simpleoncall.views.create_team', name='create-team'),
    url(r'^team/select', 'simpleoncall.views.select_team', name='select-team'),
    url(r'^team/invite', 'simpleoncall.views.invite_team', name='invite-team'),
    url(r'^key/create', 'simpleoncall.views.create_key', name='create-key'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(api.urlpatterns, namespace='api')),
)
