# -*- coding: utf-8 -*-
import sys, os
from decouple import config, Csv
from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

APPEND_SLASH = True

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.admin",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    'django.contrib.gis',
    'django.contrib.humanize',

    "easy_thumbnails",
    'geoposition',
    'social_django',
    
    'django_extensions',  

    'breed.activities',
    'breed.authentication',
    'breed.core',
    'breed.breeds',
    'breed.messenger',
    'breed.questions',
    'breed.search',
]

MIDDLEWARE = [

    # Common middlewares
    'django.middleware.security.SecurityMiddleware',
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",

    # Only needed by django admin
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'social_django.middleware.SocialAuthExceptionMiddleware', 
]

ROOT_URLCONF = "breed.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                'social_django.context_processors.backends',  
                'social_django.context_processors.login_redirect',                 
            ],
        }
    },
]

WSGI_APPLICATION = 'settings.wsgi.application'

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DATABASES = {
    "default": {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
    },
}


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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

MEDIA_URL = "/media/"
STATIC_URL = "/static/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_DIRS = (
   os.path.join(BASE_DIR, "static"),
)

# Default configuration for reverse proxy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")


THN_LOGO_VERY_SMALL_SIZE = 40       # 40x40 pixels
THN_AVATAR_SIZE = 80                # 80x80 pixels
THN_AVATAR_BIG_SIZE = 300           # 300x300 pixels
THN_LOGO_SMALL_SIZE = 80            # 80x80 pixels
THN_LOGO_BIG_SIZE = 300             # 300x300 pixels
THN_TIMELINE_IMAGE_SIZE = 640       # 640x??? pixels
THN_CARD_IMAGE_WIDTH = 300          # 300 pixels
THN_CARD_IMAGE_HEIGHT = 200         # 200 pixels
THN_PREVIEW_IMAGE_WIDTH = 800       # 800 pixels

THN_LOGO_VERY_SMALL = "logo--very-small"
THN_AVATAR_SMALL = "avatar"
THN_AVATAR_BIG = "big-avatar"
THN_LOGO_SMALL = "logo-small"
THN_LOGO_BIG = "logo-big"
THN_ATTACHMENT_TIMELINE = "timeline-image"
THN_ATTACHMENT_CARD = "card-image"
THN_ATTACHMENT_PREVIEW = "preview-image"

THUMBNAIL_ALIASES = {
    "": {
        THN_LOGO_VERY_SMALL: {"size": (THN_LOGO_VERY_SMALL_SIZE, THN_LOGO_VERY_SMALL_SIZE), "crop": True},
        THN_AVATAR_SMALL: {"size": (THN_AVATAR_SIZE, THN_AVATAR_SIZE), "crop": True},
        THN_AVATAR_BIG: {"size": (THN_AVATAR_BIG_SIZE, THN_AVATAR_BIG_SIZE), "crop": True},
        THN_LOGO_SMALL: {"size": (THN_LOGO_SMALL_SIZE, THN_LOGO_SMALL_SIZE), "crop": True},
        THN_LOGO_BIG: {"size": (THN_LOGO_BIG_SIZE, THN_LOGO_BIG_SIZE), "crop": True},
        THN_ATTACHMENT_TIMELINE: {"size": (THN_TIMELINE_IMAGE_SIZE, 0), "crop": True},
        THN_ATTACHMENT_CARD: {"size": (THN_CARD_IMAGE_WIDTH, THN_CARD_IMAGE_HEIGHT), "crop": True},
        THN_ATTACHMENT_PREVIEW: {"size": (THN_PREVIEW_IMAGE_WIDTH, 0), "crop": False},
    },
}


LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'settings'

ALLOWED_SIGNUP_DOMAINS = ['*']

FILE_UPLOAD_TEMP_DIR = '/tmp/'
FILE_UPLOAD_PERMISSIONS = 0o644

GEOPOSITION_GOOGLE_MAPS_API_KEY = 'AIzaSyBtRJpb2cKEh1B06PQX6D3bxlP61Baw5oA'

GEOPOSITION_MAP_OPTIONS = {
    'minZoom': 12,
    'maxZoom': 20,
}

GEOPOSITION_MARKER_OPTIONS = {
    'cursor': 'move'
}

AUTHENTICATION_BACKENDS = (
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)


SOCIAL_AUTH_TWITTER_KEY = 'hkHJOSR0AJu9Y6Aklup2NFyE2'
SOCIAL_AUTH_TWITTER_SECRET = 'mRtao55eHZRJFGY1eKVkqvGBAGXLwpIIJ7MHfVNaYMJbOYALhB'

SOCIAL_AUTH_FACEBOOK_KEY = '2253053394956912' 
SOCIAL_AUTH_FACEBOOK_SECRET = '833127b87bdba33fe95929c015c28cc0'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '463912647232-esbn26umeecfmlg3ddvh9p8anvo3vffo.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'qgtqa8-YIlOxOxD58Fi4y9v7'

# NOTE: DON'T INSERT MORE SETTINGS AFTER THIS LINE
TEST_RUNNER="django.test.runner.DiscoverRunner"

if "test" in sys.argv:
    print ("\033[1;91mNo django tests.\033[0m")
    print ("Try: \033[1;33mpy.test\033[0m")
    sys.exit(0)
