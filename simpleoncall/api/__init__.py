from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', 'simpleoncall.api.views.index', name='api-index'),
    url(r'^v1/oncall$', 'simpleoncall.api.views.v1_get_oncall', name='api-oncall'),
    url(r'^v1/event/create$', 'simpleoncall.api.views.v1_event_create', name='api-event-create'),
    url(r'^v1/events/(?P<status>\w+)$', 'simpleoncall.api.views.v1_events_status', name='api-events-status'),
)
