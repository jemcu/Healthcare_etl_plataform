"""
HealthAnalytics IPS — Settings principal
"""
import dj_database_url
import os
from pathlib import Path
from datetime import timedelta

try:
    from decouple import config, Csv
except ModuleNotFoundError:
    # Fallback mínimo si no está instalada python-decouple.
    def config(key, default=None, cast=None):
        val = os.environ.get(key, default)
        if cast is not None:
            return cast(val)
        return val

    class Csv(list):
        def __call__(self, value):
            if value is None:
                return []
            return [v.strip() for v in str(value).split(',') if v.strip()]


# ── Rutas base ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent   # backend/
ROOT_DIR = BASE_DIR.parent                           # raíz del proyecto

# Garantizar que python-decouple use la .env de la raíz.
# (Algunas ejecuciones pueden cambiar el cwd y hacer que python-decouple no encuentre el archivo).
ENV_PATH = ROOT_DIR / '.env'
if ENV_PATH.exists():
    os.environ.setdefault('ENV_PATH', str(ENV_PATH))


# ── Seguridad ─────────────────────────────────────────────────────────────────
SECRET_KEY = config('SECRET_KEY', default='django-insecure-cambia-esto-en-produccion-ahora')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default=".onrender.com,localhost,127.0.0.1",
    cast=Csv(),
)

# ── Aplicaciones instaladas ───────────────────────────────────────────────────
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
]

LOCAL_APPS = [
    'app.authentication',
    'app.patients',
    'app.etl',
    'app.analytics',
    'app.ml',
    'app.reports',
    'app.dashboard',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ── Middleware ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# ── Templates ─────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ROOT_DIR / 'frontend' / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

# ── Base de datos ─────────────────────────────────────────────────────────────
DB_ENGINE = config('DB_ENGINE', default='django.db.backends.postgresql')

DATABASES = {
    "default": dj_database_url.parse(
        config("SUPABASE_URL")
    )
}

# ── Modelo de usuario personalizado ──────────────────────────────────────────
AUTH_USER_MODEL = 'authentication.CustomUser'

# ── Validación de contraseñas ─────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internacionalización ──────────────────────────────────────────────────────
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ── Archivos estáticos y media ────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [ROOT_DIR / 'frontend' / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Django REST Framework ───────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# ── JWT ───────────────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://localhost:5500,http://127.0.0.1:5500',
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ── Swagger / OpenAPI ─────────────────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    'TITLE': 'HealthAnalytics IPS API',
    'DESCRIPTION': 'Plataforma Inteligente de Analítica Clínica para Detección de Riesgo Médico',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [{'BearerAuth': []}],
}

# ── Datasets y modelos ML ─────────────────────────────────────────────────────
DATASET_DIR = ROOT_DIR / 'dataset' / 'raw'
ML_MODELS_DIR = ROOT_DIR / 'ml_models'

DATASET_DIR.mkdir(parents=True, exist_ok=True)
ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)

# ── Logging ───────────────────────────────────────────────────────────────────
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} — {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file_etl': {
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'etl.log',
            'formatter': 'verbose',
        },
        'file_ml': {
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'ml.log',
            'formatter': 'verbose',
        },
        'file_general': {
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'app.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'etl': {
            'handlers': ['console', 'file_etl'],
            'level': 'INFO',
            'propagate': False,
        },
        'ml': {
            'handlers': ['console', 'file_ml'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['console', 'file_general'],
            'level': 'WARNING',
            'propagate': True,
        },
        '': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
        },
    },
}

