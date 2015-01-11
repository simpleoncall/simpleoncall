from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^login$', 'simpleoncall.internal.views.login', name='login'),
    url(r'^register$', 'simpleoncall.internal.views.register', name='register'),
)
