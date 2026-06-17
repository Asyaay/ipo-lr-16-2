import os
from pathlib import Path
import dj_database_url  # === ЗАДАНИЕ 2: ИМПОРТ ПАРСЕРА СТРОК ПОДКЛЮЧЕНИЯ БД ===

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================================================================
# === ЗАДАНИЕ 2: ЧТЕНИЕ SECRET_KEY И DEBUG ИЗ СИСТЕМНЫХ ПЕРЕМЕННЫХ СРЕД ===
# =========================================================================
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-local-fallback-key-123')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# =========================================================================
# === ЗАДАНИЕ 2: НАСТРОЙКА ALLOWED_HOSTS С ВКЛЮЧЕНИЕМ ДОМЕНА *.up.railway.app ===
# =========================================================================
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.up.railway.app']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'yogaaa',  # Твое основное рабочее приложение Студии Йоги
]

# =========================================================================
# === ЗАДАНИЕ 2: ПОДКЛЮЧЕНИЕ WHITENOISEMIDDLEWARE СРАЗУ ПОСЛЕ SECURITY ===
# =========================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Сервер раздачи статических стилей в интернете
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'yogaaa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'yogaaa.wsgi.application'
# =========================================================================
# === ЗАДАНИЕ 2 И ЗАДАНИЕ 4: КОНФИГУРАЦИЯ СУБД POSTGRESQL ЧЕРЕЗ DJ_DATABASE_URL ===
# =========================================================================
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'db.sqlite3')}"),
        conn_max_age=600
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Minsk'
USE_I18N = True
USE_TZ = True

# Конфигурация сборщика статики для корректной работы стилей сайта в интернете
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# =========================================================================
# === ЗАДАНИЕ 2: УСТАНОВКА ФЛАГОВ БЕЗОПАСНОСТИ ДЛЯ КУКИ СЕССИЙ ПРИ DEBUG=FALSE ===
# =========================================================================
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'