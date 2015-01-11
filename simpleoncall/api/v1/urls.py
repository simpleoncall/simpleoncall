from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^$', 'simpleoncall.api.v1.views.index', name='index'),
    url(r'^whose/oncall$', 'simpleoncall.api.v1.views.whose_oncall', name='whose-oncall'),
)
