import os
from datetime import timedelta
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("DJANGO_SECRET_KEY")

# Регистрация приложений
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # Сторонние библиотеки
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    
    # Локальные приложения проекта
    "user",
    "train_station",
    "orders",
]

MIDDLEWARE = [
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

# Указываем Django использовать нашу кастомную модель пользователя
AUTH_USER_MODEL = "user.User"

# Настройка подключения к базе данных (PostgreSQL с фолбеком на SQLite для тестов)
DB_HOST = os.environ.get("DB_HOST")

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
    # Если переменные окружения не заданы, проект запустится на SQLite (удобно для быстрой разработки)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "String": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }

# Настройки Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # По умолчанию закрываем все эндпоинты на чтение/запись для анонимов. 
    # Вьюсеты, требующие кастомных доступов, переопределят это поле.
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Конфигурация JWT Токенов
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Настройки Swagger документации
SPECTACULAR_SETTINGS = {
    "TITLE": "Railway Station API Service",
    "DESCRIPTION": "API system for train journeys, crews, routes, and ticket ordering.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}