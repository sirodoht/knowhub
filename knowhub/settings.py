"""
Django settings for knowhub project.

Generated by 'django-admin startproject' using Django 2.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "secret")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.environ.get("NODEBUG") is None else False

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "knowhub.app"]

ADMINS = [("Theodore", "theodorekeloglou@gmail.com")]

# Application definition

INSTALLED_APPS = [
    "main.apps.MainConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
]

if not DEBUG:
    INSTALLED_APPS.append("raven.contrib.django.raven_compat")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "main.middleware.TimezoneMiddleware",
    "main.middleware.AnalyticsMiddleware",
    # "main.middleware.BillingMiddleware",
    # "main.middleware.StatsMiddleware",
]

if DEBUG:
    MIDDLEWARE.append("main.middleware.StatsMiddleware")

ROOT_URLCONF = "knowhub.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "main.context_processors.timezone",
            ]
        },
    }
]

WSGI_APPLICATION = "knowhub.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {"default": {"ENGINE": "django.db.backends.postgresql"}}

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES["default"].update(db_from_env)

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = False

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "_static")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# Email
# https://docs.djangoproject.com/en/2.0/topics/email/

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = "email-smtp.eu-west-1.amazonaws.com"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587

DEFAULT_FROM_EMAIL = "KnowHub <hi@knowhub.app>"


# Authentication backends
# https://docs.djangoproject.com/en/2.0/topics/auth/customizing/

AUTHENTICATION_BACKENDS = (
    "main.auth_backends.EmailTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
)

LOGIN_URL = "main:login"
LOGIN_REDIRECT_URL = "main:index"
LOGOUT_REDIRECT_URL = "main:index"

AUTH_TOKEN_DURATION = 30 * 60  # = 1800 = 30 min in seconds


# Session
# https://docs.djangoproject.com/en/2.0/topics/http/sessions/

SESSION_COOKIE_AGE = 31536000  # 365 * 24 * 60 * 60 = 1 year in seconds


# Security middleware
# https://docs.djangoproject.com/en/2.0/ref/middleware/#module-django.middleware.security

if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "DENY"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 365 * 24 * 60 * 60 = 1 year in seconds
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True


# Sentry
# https://docs.sentry.io/clients/python/integrations/django/

RAVEN_CONFIG = {"dsn": os.getenv("SENTRY_DSN")}


# Logging
# https://docs.djangoproject.com/en/2.0/topics/logging/

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {"format": "[contactor] %(levelname)s %(asctime)s %(message)s"}
    },
    "handlers": {
        # Send all messages to console
        "console": {"level": "DEBUG", "class": "logging.StreamHandler"},
        # Warning messages are sent to admin emails
        "mail_admins": {
            "level": "WARNING",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        # critical errors are logged to sentry
        "sentry": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "raven.contrib.django.handlers.SentryHandler",
        },
    },
    "loggers": {
        # This is the "catch all" logger
        "": {
            "handlers": ["console", "mail_admins", "sentry"],
            "level": "DEBUG",
            "propagate": False,
        }
    },
}


# Stripe
# https://stripe.com/docs/development

STRIPE_PUBLIC = os.environ.get("STRIPE_PUBLIC")
STRIPE_SECRET = os.environ.get("STRIPE_SECRET")

STRIPE_PLAN = "plan_DimJaxbaKOgt6m"
if not DEBUG:
    STRIPE_PLAN = "plan_DimH1uvZgYpww7"


# Celery settings
# http://docs.celeryproject.org/en/v4.2.1/django/first-steps-with-django.html

CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://@localhost:6379")
if DEBUG:
    CELERY_BROKER_URL += "/3"
else:
    CELERY_BROKER_URL += "/0"
