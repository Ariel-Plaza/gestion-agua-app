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

# SMTP para las alertas del cron generar_cobros. EMAIL_HOST_USER/PASSWORD son
# un placeholder hasta que se genere una contraseña de aplicación real en la
# cuenta de Gmail que se use para enviar (ver ADMIN_ALERT_EMAIL en base.py).
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='cron.gestionagua.placeholder@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)