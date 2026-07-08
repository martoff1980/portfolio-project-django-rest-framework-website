import os
from datetime import timedelta
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Registering applications in Django settings
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    # Django REST Framework and JWT authentication
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    # Local apps
    "user",
    "train_station",
    "orders",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ROOT_URLCONF = "railway_station_config.urls"

# Enable CORS for all origins (for development purposes)
CORS_ALLOW_ALL_ORIGINS = True

# Tell Django to use our custom user model.
AUTH_USER_MODEL = "user.User"

# Settings for database connection
# (PostgreSQL with fallback to SQLite for testing)
DB_HOST = os.environ.get("DB_HOST")

# Exclude the default value
# for the auto-increment field in Django models,
# use BigAutoField for primary keys by default,
# which is suitable for large datasets.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if DB_HOST:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "railway_db"),
            "USER": os.environ.get("DB_USER", "postgres"),
            "PASSWORD": os.environ.get("DB_PASSWORD", "postgres"),
            "HOST": DB_HOST,
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }
else:
    # If environment variables are not set,
    # the project will run on SQLite (convenient for quick development)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }

# Settings for Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # Default permission classes are set to allow authenticated users
    # to perform any action, while unauthenticated users can only read data.
    # Viewsets that require custom permissions will override this field.
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Configuration for JWT Tokens
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Settings for Swagger documentation using drf-spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "Railway Station API Service",
    "DESCRIPTION": (
        "API system for train journeys, crews, routes, and ticket ordering."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

STATIC_URL = "static/"
