from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', 'simpleoncall.api.views.index', name='index'),
)
