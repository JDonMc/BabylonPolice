# coding=<utf-8>
# Copyright Aden Handasyde 2019

"""
Django settings for mysite project.
Generated by 'django-admin startproject' using Django 2.0.7.
For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import psycopg2
DEFAULT_AUTO_FIELD='django.db.models.AutoField'
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STRIPE_PUBLISHABLE_KEY = os.environ['STRIPE_PUBLISHABLE_KEY']
STRIPE_SECRET_KEY = os.environ['STRIPE_SECRET_KEY']
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/
from django.core.management.utils import get_random_secret_key

# generating and printing the SECRET_KEY
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_random_secret_key()
COINBASE_COMMERCE_API_KEY = os.environ['COINBASE_COMMERCE_API_KEY']
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# Application definition

SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'mptt',
    'Bable',
    'paypal.standard.ipn', # django-paypal
    'markdownify',
    'rest_framework',
    'rest_framework.authtoken',
    'coreapi',
]



MIDDLEWARE = [
    # 'sslify.middleware.SSLifyMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
LOCALE_PATHS = (BASE_DIR + '/locale',)
ROOT_URLCONF = 'mysite.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]



WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # brew services start postgresql
        # createdb db
        # psql db
        # CREATE USER default WITH SUPERUSER PASSWORD 'default'
        # \q
        # issues in psycopg2: makemigrations Bable
        'NAME': 'db',                                                   
        'USER': 'jackmclovin',                                                   
        'PASSWORD': 'default',                                      
        'HOST': '127.0.0.1',                                                     
        'PORT': '5432',  
    }
}

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

LOGIN_URL = '/B/index/'
LOGOUT_REDIRECT_URL = '/B/index/'

'''
AUTHENTICATION_BACKENDS = (
    'Bable.auth_backends.CustomUserModelBackend',
)
CUSTOM_USER_MODEL = 'models.Anon'
'''

# https://stackoverflow.com/questions/31324005/django-1-8-sending-mail-using-gmail-smtp

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.mailgun.com'
EMAIL_HOST_USER = 'jackdonmclovin@gmail.com'
'''
Keep out of Open Source
'''
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_PORT = 587

# https://www.youtube.com/watch?v=Z5dBopZWOzo
#django-paypal settings
# https://github.com/tijptjik/django-paypal-subscription/blob/master/setup.py
PAYPAL_RECEIVER_EMAIL = 'kranked_354@hotmail.com'
PAYPAL_TEST = False

import dj_database_url
DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html

'''
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_ACCESS_KEY_ID = 
# AWS_SECRET_ACCESS_KEY = 
# AWS_STORAGE_BUCKET_NAME = 
AWS_DEFAULT_ACL = None
AWS_BUCKET_ACL = None
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
'''

DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = 'tower-of-bable'
GS_DEFAULT_ACL = 'publicRead'
GS_CACHE_CONTROL = 'max_age=86400'

#from google.cloud import storage

#GOOGLE_APPLICATION_CREDENTIALS = storage.Client.from_service_account_json(os.path.join(os.path.dirname(os.path.abspath(__file__)), "towerofbable-37-4e4d75248973.json"))


REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.TokenAuthentication',  # <-- Token Authentication
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # <-- JWT Authentication
    ],
}