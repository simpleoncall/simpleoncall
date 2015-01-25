from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', 'simpleoncall.api.v1.views.index', name='index'),
    url(r'^whose/oncall$', 'simpleoncall.api.v1.views.whose_oncall', name='whose-oncall'),
    url(r'^alert/add$', 'simpleoncall.api.v1.views.alert_create', name='alert-add'),
    url(r'^alert/update$', 'simpleoncall.api.v1.views.alert_update', name='alert-update'),
    url(r'^alerts$', 'simpleoncall.api.v1.views.alerts_list', name='alerts-list'),
    url(r'^integration/datadog$', 'simpleoncall.api.v1.views.datadog_integration', name='integration-datadog'),
)
