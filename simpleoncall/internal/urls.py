from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^login$', 'simpleoncall.internal.views.login', name='login'),
    url(r'^register$', 'simpleoncall.internal.views.register', name='register'),
    url(r'^account/info$', 'simpleoncall.internal.views.account_info', name='account-info'),
    url(r'^account/password$', 'simpleoncall.internal.views.account_password', name='account-password'),
    url(r'^account/alerts$', 'simpleoncall.internal.views.account_alerts', name='account-alerts'),
    url(r'^team/invite$', 'simpleoncall.internal.views.team_invite', name='team-invite'),
    url(r'^api-key/create$', 'simpleoncall.internal.views.api_key_create', name='api-key-create'),
    url(r'^api-key/update$', 'simpleoncall.internal.views.api_key_update', name='api-key-update'),
    url(r'^api-key/deactivate$', 'simpleoncall.internal.views.api_key_deactivate', name='api-key-deactivate'),
    url(r'^api-key/activate$', 'simpleoncall.internal.views.api_key_activate', name='api-key-activate'),
)
