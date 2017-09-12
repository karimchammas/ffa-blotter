"""
Django settings for zipline_project project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8rk=0@$^cy6^)2j=@p^^o@4%4wa2%nt05efp0zp9p0)(jx8ais'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'zipline_app.apps.ZiplineAppConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'bootstrap3',
    'pagination_bootstrap',
    'django_select2',
    'django_tables2',
    'django_filters',
    'reversion',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'zipline_app.login_required_middleware.LoginRequiredMiddleware',
    'pagination_bootstrap.middleware.PaginationMiddleware',
]

ROOT_URLCONF = 'zipline_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # pagination configuration
                # https://github.com/staticdev/django-pagination-bootstrap#configuration
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'zipline_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Beirut'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

# django logging
# https://docs.djangoproject.com/en/1.10/topics/logging/#examples
import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'zipline_app': {
            'handlers': ['console'],
            'level': os.getenv('POLLS_LOG_LEVEL', 'INFO'),
        },
    },
}

from django.urls import  reverse_lazy
LOGIN_URL = reverse_lazy('login')
# copy from /home/shadi/.local/share/virtualenvs/ZL2/lib/python3.5/site-packages/django/contrib/auth/urls.py
auth_urls = ['login', 'logout', 'password_change', 'password_reset', 'reset']
LOGIN_EXEMPT_URLS = ['^$'] + ['^%s'%(x) for x in auth_urls]
LOGIN_REDIRECT_URL = '/'

# sending email with django
# https://docs.djangoproject.com/en/1.10/topics/email/
DEFAULT_FROM_EMAIL  = os.getenv("DEFAULT_FROM_EMAIL", None)
EMAIL_SUBJECT_PREFIX= "[Blotter] "
if False:
  EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
  # EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
  EMAIL_BACKEND       = 'django_smtp_ntlm_backend.NTLMEmail'
  EMAIL_HOST          = os.getenv("EMAIL_HOST", None)
  EMAIL_PORT          = os.getenv("EMAIL_PORT", None)
  EMAIL_HOST_USER     = os.getenv("EMAIL_HOST_USER", None)
  EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", None)
  EMAIL_USE_TLS       = False
  EMAIL_USE_SSL       = False

#
BASE_URL = os.getenv("BASE_URL", "")

# Mayan EDMS credentials
MAYAN_HOST           = os.getenv("MAYAN_HOST",           None)
MAYAN_ADMIN_USER     = os.getenv("MAYAN_ADMIN_USER",     None)
MAYAN_ADMIN_PASSWORD = os.getenv("MAYAN_ADMIN_PASSWORD", None)
