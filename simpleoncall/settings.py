"""
Django settings for simpleoncall project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SIMPLEONCALL_DIR = os.path.join(BASE_DIR, 'simpleoncall')
SIMPLEONCALL_CONF = os.getenv('SIMPLEONCALL_CONF', '~/.simpleoncall/simpleoncall.py')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'zt6&@ddm%xle-@q!vflh((#a+_yh=etpmnh*vhb)phxvjzmu(a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

ALLOWED_HOSTS = ('127.0.0.1',)

BASE_URL = '127.0.0.1:8000'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'compressor',
    'simpleoncall',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'simpleoncall.auth.EmailAuthBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_FROM_ADDRESS = 'SimpleOnCall Service <service@simpleoncall.com>'

ROOT_URLCONF = 'simpleoncall.urls'

WSGI_APPLICATION = 'simpleoncall.wsgi.application'

AUTH_USER_MODEL = 'simpleoncall.User'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(SIMPLEONCALL_DIR, 'static')
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)
LIBSASS_OUTPUT_STYLE = 'nested' if DEBUG else 'compressed'

USE_BUNDLES = False
SCRIPTS = {
    'js/dashboard.min.js': (
        'js/dashboard/Chart.min.js',
        'js/dashboard/dashboard.js',
    ),
    'js/alerts.min.js': (
        'js/alerts/alerts.js',
    ),
    'js/schedule.min.js': (
        'js/schedule/schedule.js',
    ),
    'js/core.min.js': (
        'js/es5-shim.js',
        'js/scant.min.js',
        'js/simpleoncall.js',
    ),
}
HTML_MINIFY = True

BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

if SIMPLEONCALL_CONF:
    path = os.path.abspath(os.path.expanduser(SIMPLEONCALL_CONF))
    if os.path.exists(path):
        with open(path) as fp:
            import imp
            imp.load_module('simpleoncall.settings', fp, path, ('.py', 'r', 1))
