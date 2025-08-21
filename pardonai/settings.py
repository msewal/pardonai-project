"""
Django settings for pardonai project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# DEBUG mode based on environment variable
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"

# Allowed hosts configuration
ALLOWED_HOSTS = [
    "127.0.0.1", "localhost",
    os.getenv("APP_HOST", ""),      # e.g., app.example.com
    os.getenv("AWS_HOST", ""),      # e.g., ec2-xx-xx-xx-xx.compute.amazonaws.com
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Core Apps
    'pardonai.dashboard',  # Core app - temel modeller ve choice sınıfları
    
    # Business Apps
    'accounts',
    'pardonai.businesses',  # İşletme yönetimi
    'pardonai.menu',        # Menü ve ürün yönetimi
    'pardonai.dealers',     # Bayi ve deneyim yönetimi
    'pardonai.orders',      # Sipariş kayıtları
    'pardonai.performance', # Performans metrikleri
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # WhiteNoise for static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = 'pardonai.urls'


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],   # Project's templates directory
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]},
    },
]

WSGI_APPLICATION = 'pardonai.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pardonai_db',
        'USER': 'melek',
        'PASSWORD': 'Pa55_word123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'tr-tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"   # collectstatic output directory
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files (uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

import os

# Define the templates directory
templates_dir = os.path.join("c:\\Users\\Melek\\source\\repos\\pardonai-project", "templates")

# Function to add {% load static %} to templates
def add_load_static_to_templates(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                with open(file_path, "r+", encoding="utf-8") as f:
                    content = f.read()
                    if "{% load static %}" not in content:
                        # Add {% load static %} at the top of the file
                        f.seek(0, 0)
                        f.write("{% load static %}\n" + content)
                        print(f"Updated: {file_path}")

# Run the function
add_load_static_to_templates(templates_dir)
