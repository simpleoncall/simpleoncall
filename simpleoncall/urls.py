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
    url(r'^invite/accept', 'simpleoncall.views.invite_accept', name='invite-accept'),
    url(r'^key/create', 'simpleoncall.views.create_key', name='create-key'),
    url(r'^event/ack/(?P<event_id>[0-9a-z]+)', 'simpleoncall.views.event_ack', name='event-ack'),
    url(r'^event/resolve/(?P<event_id>[0-9a-z]+)', 'simpleoncall.views.event_resolve', name='event-resolve'),
    url(r'^event/view/(?P<event_id>[0-9a-z]+)', 'simpleoncall.views.event_view', name='event_view'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(api.urlpatterns, namespace='api')),
)
