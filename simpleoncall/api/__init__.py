from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', 'simpleoncall.api.views.index', name='api-index'),
    url(r'^oncall$', 'simpleoncall.api.views.get_oncall', name='api-oncall'),
    url(r'^event/create$', 'simpleoncall.api.views.event_create', name='api-event-create'),
    url(r'^events/(?P<status>\w+)$', 'simpleoncall.api.views.events_status', name='api-events-status'),
)
