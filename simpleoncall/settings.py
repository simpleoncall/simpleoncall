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

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'zt6&@ddm%xle-@q!vflh((#a+_yh=etpmnh*vhb)phxvjzmu(a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'simpleoncall',
)

MIDDLEWARE_CLASSES = (
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

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(SIMPLEONCALL_DIR, 'static')
USE_BUNDLES = False
STYLESHEETS = {
    'css/core.min.css': (
        'css/pure/pure.css',
        'css/pure/grids-responsive.css',
        'css/base.css',
        'css/menu.css',
        'css/header.css',
        'css/forms.css',
        'css/tabs.css',
    ),
}
SCRIPTS = {
    'js/dashboard.min.js': (
        'js/d3/d3.min.js',
        'js/epoch/epoch.min.js',
        'js/dashboard/dashboard.js',
    ),
}
