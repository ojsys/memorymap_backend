import pymysql
pymysql.install_as_MySQLdb()

from .base import *
from decouple import config as default_config, RepositoryEnv, Config
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR is defined in base.py, which is imported above.
# We assume .env is in the project root, one level above backend/config/settings/
# BASE_DIR in base.py points to the `backend` directory.
# So BASE_DIR.parent will point to the project root `mapping_memory`.

# Explicitly load .env file
# Check if .env file exists before loading
env_path = BASE_DIR.parent / '.env'
if env_path.exists():
    config = Config(RepositoryEnv(str(env_path))) # Create a new Config instance using RepositoryEnv
else:
    config = default_config # Fallback to default config if .env not found

SECRET_KEY = config('SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='3306', cast=int),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
    }
}

CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=lambda v: [s.strip() for s in v.split(',')])
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=lambda v: [s.strip() for s in v.split(',')])

# Security hardening
# cPanel terminates SSL before the request reaches Django, so we must NOT redirect
# here (it would loop). Let Apache/cPanel enforce HTTPS at the server level.
SECURE_SSL_REDIRECT = False
# Tell Django to trust the X-Forwarded-Proto header set by cPanel's proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

