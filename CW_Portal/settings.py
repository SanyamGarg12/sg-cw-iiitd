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

import credentials

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = credentials.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

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
    'studentportal',
    'supervisor',
    'djrill',

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

DATABASES = {
    # 'default': {
    #    'ENGINE': 'django.db.backends.sqlite3',
    #    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # },
    'default': {
        # TODO: Change values here
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cw_portal',
        'USER': 'cw',
        'PASSWORD': 'test',
        # 'NAME': os.environ['DB_NAME'],
        # 'USER': os.environ['DB_USER'],
        # 'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': 'localhost',  # Or an IP Address that your DB is hosted on WILL CHANGE
        'PORT': '3306',
    }
}

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

EMAIL_USE_TLS = True

ALLOWED_DOMAINS = ['iiitd.ac.in']

SOCIALACCOUNT_ADAPTER = 'studentportal.adapters.DomainLoginAdapter'
ACCOUNT_ADAPTER = 'studentportal.adapters.NoMessagesLoginAdapter'
MAXIMUM_UPLOAD_SIZE_ALLOWED = 10
EMAIL_HOST_USER = credentials.EMAIL_HOST_USER

EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
MANDRILL_API_KEY = credentials.MANDRILL_API_KEY
LnF404_url = credentials.LnF404_url
LnF404_SiteID = credentials.LnF404_SiteID
LnF404_token = credentials.LnF404_token

ALLOWED_HOSTS = ['*']
