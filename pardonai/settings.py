
from pathlib import Path
import os
import environ
from django.core.exceptions import ImproperlyConfigured

# ------------------------------------------------------------------------------
# Base
# ------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# .env yükle (proje kökünde .env beklenir)
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

def env_required(key: str) -> str:
    """Zorunlu ortam değişkeni yoksa anlaşılır bir hata ver."""
    val = env(key, default=None)
    if val in (None, ""):
        raise ImproperlyConfigured(f"Environment variable '{key}' is required.")
    return val

# ------------------------------------------------------------------------------
# Security
# ------------------------------------------------------------------------------
SECRET_KEY = env_required("SECRET_KEY")          # .env zorunlu
DEBUG = env.bool("DJANGO_DEBUG", default=False)

# Gizli değil ama ortamdan gelebilir; local için makul varsayılan bırakıyoruz
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])

# CSRF trusted origins: .env’de tanımlıysa onu kullan; yoksa ALLOWED_HOSTS’tan üret
default_trusted = []
for host in ALLOWED_HOSTS:
    if host not in ("localhost", "127.0.0.1", ""):
        default_trusted.extend([f"http://{host}", f"https://{host}"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=default_trusted)

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

    # Core
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
    "whitenoise.middleware.WhiteNoiseMiddleware",   # Static dosyalar
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
# Tercih: DATABASE_URL (örn: postgres://user:pass@host:5432/dbname)
# Alternatif: POSTGRES_* değişkenleri (hepsi zorunlu). Defaultsuz!
# ------------------------------------------------------------------------------
db_url = env("DATABASE_URL", default=None)
if db_url:
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env_required("POSTGRES_DB"),
            "USER": env_required("POSTGRES_USER"),
            "PASSWORD": env_required("POSTGRES_PASSWORD"),
            "HOST": env("POSTGRES_HOST", default="localhost"),
            "PORT": env("POSTGRES_PORT", default="5432"),
        }
    }

DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)

# ------------------------------------------------------------------------------
# I18N / TZ
# ------------------------------------------------------------------------------
LANGUAGE_CODE = "tr-tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------------------
# Static / Media (Whitenoise)
# ------------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------------------------------------
# Prod güvenlik (DEBUG=False)
# ------------------------------------------------------------------------------
if not DEBUG:
    SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)  # HTTPS yoksa False
    CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=False)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    # LB/Proxy arkasında isen aç:
    # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
