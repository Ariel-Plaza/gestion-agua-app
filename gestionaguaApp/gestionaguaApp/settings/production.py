from .base import *
from decouple import config
import dj_database_url

SECRET_KEY = config('SECRET_KEY_PROD')

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])


DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
    )
}

STATIC_ROOT = BASE_DIR / 'static'

CORS_ALLOWED_ORIGINS = [
    "https://sistema-agua.arielplaza.dev",
]

CSRF_TRUSTED_ORIGINS = [
    "http://146.235.242.0",
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True