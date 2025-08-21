"""
Django settings for pardonai project.
"""

from pathlib import Path
import os
import environ

# ------------------------------------------------------------------------------
# Base
# ------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# .env yükle (proje kökünde .env dosyası bekler)
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

# ------------------------------------------------------------------------------
# Security
# ------------------------------------------------------------------------------
SECRET_KEY = env("SECRET_KEY", default="!!!-CHANGE-ME-!!!")

# Production'da DEBUG False
DEBUG = env.bool("DJANGO_DEBUG", default=False)

# ALLOWED_HOSTS: .env içinde virgülle ayrılmış listeyi destekler
ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["127.0.0.1", "localhost", "51.20.31.215"],
)

# CSRF için güvenilir origin’ler (http/https domain ya da IP)
# .env içinde CSRF_TRUSTED_ORIGINS tanımlıysa onu kullan; yoksa ALLOWED_HOSTS'tan üret
DEFAULT_TRUSTED = []
for h in ALLOWED_HOSTS:
    if h not in ("localhost", "127.0.0.1", ""):
        DEFAULT_TRUSTED.extend([f"http://{h}", f"https://{h}"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=DEFAULT_TRUSTED)

# ------------------------------------------------------------------------------
# Apps
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Core Apps
    "pardonai.dashboard",

    # Business Apps
    "accounts",
    "pardonai.businesses",
    "pardonai.menu",
    "pardonai.dealers",
    "pardonai.orders",
    "pardonai.performance",
]

# ------------------------------------------------------------------------------
# Middleware
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # Static file serving
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "pardonai.urls"

# ------------------------------------------------------------------------------
# Templates
# ------------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "pardonai.wsgi.application"

# ------------------------------------------------------------------------------
# Database
# - Tercihen DATABASE_URL kullan (örn: postgres://user:pass@host:5432/dbname)
# - Yoksa tek tek env değişkenlerinden oku
# ------------------------------------------------------------------------------
# Örn: DATABASE_URL=postgres://melek:Pa55_word123@localhost:5432/pardonai_db
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"postgres://{env('POSTGRES_USER', default='melek')}:{env('POSTGRES_PASSWORD', default='Pa55_word123')}"
                f"@{env('POSTGRES_HOST', default='localhost')}:{env('POSTGRES_PORT', default='5432')}/"
                f"{env('POSTGRES_DB', default='pardonai_db')}"
    )
}
# Persistent connections
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)

# ------------------------------------------------------------------------------
# Password validation
# ------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------------------------------------------------------
# Internationalization
# ------------------------------------------------------------------------------
LANGUAGE_CODE = "tr-tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------------------
# Static files (Whitenoise ile)
# ------------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"     # collectstatic çıktısı
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ------------------------------------------------------------------------------
# Media files
# ------------------------------------------------------------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ------------------------------------------------------------------------------
# Default PK
# ------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------------------------------------
# Prod güvenlik ayarları (DEBUG=False ise)
# ------------------------------------------------------------------------------
if not DEBUG:
    SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)  # HTTPS yoksa False bırak
    CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=False)        # HTTPS yoksa False bırak
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    # SSL arkasında çalışıyorsan (Load Balancer vb.):
    # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ------------------------------------------------------------------------------
# Logging (gunicorn/stdout'a hata bas)
# ------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
