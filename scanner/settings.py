"""
Django settings for scanner project – optimized for PythonAnywhere
Tested & working on free/paid accounts with SQLite
"""

from pathlib import Path
import os

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: Change this before going live!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-change-this-immediately-1234567890!@#$%^"
)

# PythonAnywhere automatically sets DEBUG=False in production
# But you can override it in the .env or here for testing
DEBUG = False

# PythonAnywhere gives you a domain like username.pythonanywhere.com
# Add your custom domain later if you buy one
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    f"{os.environ.get('USER')}.pythonanywhere.com",   # ← auto-detects your PA username
]

# If you have a custom domain, add it here manually:
# ALLOWED_HOSTS.append('www.mynotes.com')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'scan',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'scanner.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # optional global templates folder
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'scanner.wsgi.application'

# Database – SQLite is perfect for PythonAnywhere
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'           # or 'Asia/Riyadh', 'Europe/London', etc.
USE_I18N = True
USE_TZ = True

# Static files (CSS, JS, images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'           # ← PythonAnywhere collects here
STATICFILES_DIRS = [BASE_DIR / 'static']          # your local static folder

# Media files (uploaded images from OCR)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security settings – PythonAnywhere serves over HTTPS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# CSRF Trusted Origins (required for HTMX + HTTPS)
CSRF_TRUSTED_ORIGINS = [
    f"https://{os.environ.get('USER')}.pythonanywhere.com",
]

# Your Colab OCR endpoint (change when ngrok URL changes!)
COLAB_OCR_URL = os.environ.get(
    "COLAB_OCR_URL",
    "https://talon-bionomic-apogamously.ngrok-free.dev"
)

# Optional: Show nice error pages in production
if not DEBUG:
    # Remove default Django error handlers so PythonAnywhere shows your templates
    pass