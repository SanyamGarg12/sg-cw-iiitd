"""
Django settings for CW_Portal project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import json
import os

import dj_database_url
import django

import credentials
SECRET_KEY = credentials.SECRET_KEY
# django.setup()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = DEBUG

TEMPLATE_DIRS = (
    BASE_DIR + '/studentportal/templates/',
)

MEDIA_ROOT = BASE_DIR + '/media/'
MEDIA_URL = '/media/'

SITE_ID = 1

# Application definition

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'studentportal.apps.StudentportalConfig',
    'supervisor.apps.SupervisorConfig',

    # There's a reason for why these following apps
    # have been commented out.
    # While setting up the project, these apps are essential
    # for building up the models needed and should be uncommented
    # out. However, once the migrations for these apps have been
    # synced, `allauth.socialaccount.providers.*` apps can handle
    # the login magic logic on their own. These apps, rather,
    # add a bit of exploits, because going to specific urls
    # lead to the pages of these apps, which have the options
    # of resetting passwords.
    # ---
    'social_django',
    'allauth',
    'social.apps.django_app.default',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers',
    # ---

    'allauth.socialaccount.providers.google',
    'bootstrapform',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
)

ROOT_URLCONF = 'CW_Portal.urls'

WSGI_APPLICATION = 'CW_Portal.wsgi.application'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    'social_core.backends.google.GoogleOAuth2'
)

# TEMPLATE_CONTEXT_PROCESSORS = (
#     "django.core.context_processors.request",
#     "django.contrib.auth.context_processors.auth",
#     "allauth.account.context_processors.account",
#     "allauth.socialaccount.context_processors.socialaccount",
#     "django.contrib.messages.context_processors.messages",
# )

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
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                # "allauth.socialaccount.context_processors.socialaccount",
                # "allauth.account.context_processors.account",
                # "django.core.context_processors.request",
            ],
        },
    },
]

LOGIN_REDIRECT_URL = '/first_login/'
LOGIN_URL = '/accounts/google/login/'
LOGOUT_URL = '/logout/'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = credentials.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = credentials.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
SOCIAL_AUTH_URL_NAMESPACE = 'social'

SOCIALACCOUNT_QUERY_EMAIL = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            #     'https://www.googleapis.com/auth/plus.login',
            #     'https://www.googleapis.com/auth/plus.me'
        ],
        'AUTH_PARAMS': {'access_type': 'online'}
    }
}

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DB_URL = credentials.DATABASE_URL
DATABASES = {'default': dj_database_url.parse(DB_URL, conn_max_age=600)}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Calcutta'

USE_I18N = True

USE_L10N = True

USE_TZ = False

APPEND_SLASH = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

STATISTICS_FOLDER_NAME = credentials.STATISTICS_FOLDER_NAME
UPLOAD_PATH = 'uploads/%Y/'
STATICFILES_DIR = (
    os.path.join(
        BASE_DIR,
        'static',
    ),
)
CACHES = {
    'default': {
        'TIMEOUT': None,
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}


ALLOWED_DOMAINS = ['iiitd.ac.in']

SOCIALACCOUNT_ADAPTER = 'studentportal.adapters.DomainLoginAdapter'
ACCOUNT_ADAPTER = 'studentportal.adapters.NoMessagesLoginAdapter'
MAXIMUM_UPLOAD_SIZE_ALLOWED = 10

# Please enable "Allow Less Secure Apps" in your Gmail account to enable mailing
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587

EMAIL_HOST_USER = credentials.EMAIL_SG_USER
EMAIL_HOST_PASSWORD = credentials.EMAIL_SG_PASSWORD

LnF404_url = credentials.LnF404_url
LnF404_SiteID = credentials.LnF404_SiteID
LnF404_token = credentials.LnF404_token

ALLOWED_HOSTS = ['192.168.1.69', 'localhost', 'sgcw.iiitd.edu.in']
AUTH_USER_MODEL = 'studentportal.CustomUser'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'django.log',
            'when': 'D',  # this specifies the interval
            'interval': 1,  # defaults to 1, only necessary for other values
            'backupCount': 30,  # how many backup file to keep, 10 days
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
