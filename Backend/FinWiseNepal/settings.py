"""
Django settings for FinWiseNepal project.
AI-powered Investment Management and NEPSE Analytics Platform.
"""

from pathlib import Path
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-v14!qotvp1j5w%*u)==sdvbo#pdd(&zi=-8_yq42wm-t+_66y0'
)

DEBUG = True
ALLOWED_HOSTS = ['*']

# ========== Installed Apps ==========
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'corsheaders',
    'rest_framework',

    # Project apps
    'authentication',
    'nepse',
    'planner',
    'portfolio',
    'reports',
]

# ========== Middleware ==========
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

ROOT_URLCONF = 'FinWiseNepal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'FinWiseNepal.wsgi.application'

# ========== Database ==========
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'finwisenepal',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# ========== Auth / Password Validators ==========
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========== Internationalization ==========
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_TZ = True

# ========== Static / Media ==========
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ========== CORS ==========
CORS_ALLOW_ALL_ORIGINS = True

# ========== Django REST Framework ==========
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

# ========== JWT Configuration ==========
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========== OpenAI API Configuration ==========
# Set your OpenAI API key here or in environment variable OPENAI_API_KEY
OPENAI_API_KEY = os.environ.get(
    'OPENAI_API_KEY',
    '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'
)

# ========== NEPSE Data Configuration ==========
NEPSE_CSV_DIR = BASE_DIR.parent / 'NEPSE.CSV'
