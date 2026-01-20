from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

# =========================
# Custom User
# =========================
AUTH_USER_MODEL = 'core.AdminUser'

# =========================
# Load environment variables
# =========================
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# Core Settings
# =========================
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-change-this-immediately"
)

DEBUG = os.environ.get("DEBUG", "False") == "True"

# =========================
# Allowed Hosts (no protocols, no ports)
# =========================
ALLOWED_HOSTS = [
    "studycompanion-fzrm.onrender.com",  # backend
    "admincarrier.netlify.app",           # primary frontend
    "studycompanions.netlify.app",        # secondary frontend
    "localhost",
    "127.0.0.1",
]

# =========================
# Installed Apps
# =========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'corsheaders',

    # Local apps
    'core',
    'scan',
    'premium_users',
]

# =========================
# API Keys
# =========================
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')

# =========================
# Middleware (ORDER MATTERS)
# =========================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # MUST be first
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# =========================
# CORS Configuration
# =========================
CORS_ALLOWED_ORIGINS = [
    "https://admincarrier.netlify.app",
    "https://studycompanions.netlify.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# Allow custom headers
from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = list(default_headers) + ['X-User-ID']

# =========================
# CSRF Configuration
# =========================
CSRF_TRUSTED_ORIGINS = [
    "https://admincarrier.netlify.app",
    "https://studycompanions.netlify.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# =========================
# URLs / Templates
# =========================
ROOT_URLCONF = "scanner.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = "scanner.wsgi.application"

# =========================
# Database
# =========================
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# =========================
# Static & Media Files
# =========================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =========================
# OCR Endpoint
# =========================
COLAB_OCR_URL = os.environ.get(
    "COLAB_OCR_URL",
    "https://talon-bionomic-apogamously.ngrok-free.dev"
)

# =========================
# Security Headers
# =========================
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# =========================
# Production Security
# =========================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# =========================
# Session / Cookie Settings (cross-domain)
# =========================
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# =========================
# Default PK
# =========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========================
# Authentication Settings
# =========================
# =========================
# Authentication Settings
# =========================
LOGIN_URL = '/backend/login/'  # Changed from 'core:admin_login'
LOGIN_REDIRECT_URL = '/backend/account/'
LOGOUT_REDIRECT_URL = '/backend/login/'
AUTH_USER_MODEL = 'core.AdminUser'
