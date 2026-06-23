from .base import *
from decouple import config
import dj_database_url

SECRET_KEY = config('SECRET_KEY_PROD')

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])

import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        env='DATABASE_URL',
        conn_max_age=600,
    )
}

STATIC_ROOT = BASE_DIR / 'staticfiles'

CORS_ALLOWED_ORIGINS = [
    "https://django-companion-app.lovable.app",
]