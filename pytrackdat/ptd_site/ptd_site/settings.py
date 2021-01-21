import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# PyTrackDat custom settings

PTD_DESIGN_FILE = os.getenv("PTD_DESIGN_FILE", "")
if not PTD_DESIGN_FILE:
    raise EnvironmentError("PTD_DESIGN_FILE must be set for PyTrackDat to run.")

PTD_SITE_URL = os.getenv("PTD_SITE_URL", "http://localhost")
PTD_SITE_NAME = os.getenv("PTD_SITE_NAME", "My Database")
PTD_GIS_MODE = os.getenv("PTD_GIS_MODE", "false").strip().lower() == "true"


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'c47tr0d5njmt7e%d3ez#3i-p!*3&e6a0t&&x+x25u5-nre)him'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not (os.getenv("DJANGO_ENV") == "production")

ALLOWED_HOSTS = ['127.0.0.1', PTD_SITE_URL] if not DEBUG else []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'pytrackdat.ptd_site.core.apps.CoreConfig',
    'pytrackdat.ptd_site.snapshot_manager.apps.SnapshotManagerConfig',

    'advanced_filters',
    'rest_framework',
    'reversion',
    'corsheaders',
] + ([
    'django.contrib.gis',
    'rest_framework_gis',
] if PTD_GIS_MODE else [])

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ptd_site.urls'

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

WSGI_APPLICATION = 'ptd_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.spatialite" if PTD_GIS_MODE else "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),  # TODO: Data directory
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,  # Default
}

CORS_ALLOWED_ORIGINS = ["http://localhost:8000", "http://localhost:8080"] if DEBUG else [PTD_SITE_URL]

SPATIALITE_LIBRARY_PATH = os.environ.get("SPATIALITE_LIBRARY_PATH", "") if DEBUG else None

DATA_UPLOAD_MAX_NUMBER_FIELDS = None


# Re-define module paths for their new hierarchy in the pytrackdat module
ROOT_URLCONF = "pytrackdat.ptd_site.ptd_site.urls"
WSGI_APPLICATION = "pytrackdat.ptd_site.ptd_site.wsgi.application"
