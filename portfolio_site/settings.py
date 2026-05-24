"""
Django settings for portfolio_site.

Переменные окружения загружаются из .env через python-dotenv.
Для локальной разработки: DB_ENGINE не задан → SQLite.
Для продакшена: задать все DATABASE_* и DEBUG=False.
"""
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Загрузка .env
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Базовые пути
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Секреты и режим отладки
# ---------------------------------------------------------------------------
# Обязательная переменная — выбрасывает KeyError при отсутствии (намеренно).
SECRET_KEY = os.environ['SECRET_KEY']

# DEBUG=True только явно заданным значением; всё остальное → False.
DEBUG = os.getenv('DEBUG', 'False').strip().lower() == 'true'

# ALLOWED_HOSTS — разделённый запятыми список; пустая строка → пустой список.
_raw_hosts = os.getenv('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts.split(',') if h.strip()]

# ---------------------------------------------------------------------------
# Приложения
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'portfolio',
]

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'portfolio_site.urls'

# ---------------------------------------------------------------------------
# Шаблоны
# ---------------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # DIRS пустой — шаблоны живут внутри приложений (APP_DIRS=True).
        'DIRS': [],
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

WSGI_APPLICATION = 'portfolio_site.wsgi.application'

# ---------------------------------------------------------------------------
# База данных
# ---------------------------------------------------------------------------
# Локальная разработка: DB_ENGINE не задан → SQLite.
# Продакшен: задать DB_ENGINE=django.db.backends.postgresql и остальные DB_*.
_db_engine = os.getenv('DB_ENGINE', '').strip()

if _db_engine:
    DATABASES = {
        'default': {
            'ENGINE': _db_engine,
            'NAME': os.environ['DB_NAME'],
            'USER': os.environ['DB_USER'],
            'PASSWORD': os.environ['DB_PASSWORD'],
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            # КОМПРОМИСС: conn_max_age=600 держит соединения открытыми.
            # При использовании PgBouncer в режиме transaction — убрать.
            'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', '600')),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ---------------------------------------------------------------------------
# Валидация паролей
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# Интернационализация
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Статика и медиа
# ---------------------------------------------------------------------------
STATIC_URL = '/static/'
# STATIC_ROOT используется командой collectstatic на проде.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Дополнительные каталоги для поиска статики (TailwindCSS output).
STATICFILES_DIRS = [
    BASE_DIR / 'portfolio' / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ---------------------------------------------------------------------------
# Разное
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Логирование
# ---------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'portfolio': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ---------------------------------------------------------------------------
# Настройки безопасности для продакшена (DEBUG=False)
# ---------------------------------------------------------------------------
if not DEBUG:
    # Принудительный редирект HTTP → HTTPS.
    SECURE_SSL_REDIRECT = True

    # HSTS: браузер запоминает HTTPS на 1 год.
    # КОМПРОМИСС: включайте preload и includeSubDomains только если уверены
    # что все поддомены тоже на HTTPS. При первом деплое можно начать с 3600.
    SECURE_HSTS_SECONDS = 31_536_000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True  # КОМПРОМИСС: необратимо до истечения срока

    # Куки сессии и CSRF передаются только по HTTPS.
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Запрет угадывания Content-Type браузером (MIME-sniffing).
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # X-Frame-Options: DENY — запрет встраивания в <iframe>.
    X_FRAME_OPTIONS = 'DENY'

    # Включить заголовок X-XSS-Protection (устаревший, но безвредный).
    SECURE_BROWSER_XSS_FILTER = True

    # КОМПРОМИСС: CSP (Content Security Policy) НЕ настраивается здесь —
    # он будет выставляться Nginx-заголовком (см. DEPLOY.md).
    # Причина: django-csp требует отдельной зависимости, а Nginx-подход
    # проще аудировать и не требует изменений в коде Python.
    #
    # Важно: django.contrib.admin использует inline-скрипты и inline-стили,
    # поэтому CSP для /admin/ потребует 'unsafe-inline' или nonce.
    # Это КОМПРОМИСС — приемлемо, т.к. /admin/ закрыт от публики.
