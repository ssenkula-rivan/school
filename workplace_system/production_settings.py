"""
Production settings for Render deployment
"""
import os
import dj_database_url
from .settings import *

# Override settings for production
DEBUG = False
ENVIRONMENT = 'production'

# Security Settings for Render
SECURE_SSL_REDIRECT = False  # Render handles SSL at edge
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_TZ = True

# CSRF Settings for Render
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
]

# Session Settings - Use database for multi-worker compatibility (CRITICAL FIX)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 3600  # 1 hour

# Database - Use Render's DATABASE_URL (CRITICAL FIX)
if 'DATABASE_URL' in os.environ:
    try:
        DATABASES = {
            'default': dj_database_url.parse(
                os.environ.get('DATABASE_URL'),
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
        # Ensure SSL is properly configured for Render PostgreSQL
        DATABASES['default']['OPTIONS'] = {
            'sslmode': 'require',
        }
        print("✅ Using Render PostgreSQL database")
    except Exception as e:
        print(f"❌ Database configuration error: {e}")
        # Don't crash - use SQLite fallback
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
        print("⚠️  Falling back to SQLite database")

# Static Files - Render compatible
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Use STORAGES dict (CRITICAL FIX - removed conflicting STATICFILES_STORAGE)
STORAGES = {
    "default": EnvironmentConfig.get_storage_config(),
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Media Files - Use Cloudflare R2 for production
use_r2 = os.environ.get('USE_R2_STORAGE', 'False').lower() == 'true'
if use_r2:
    # Media URLs for R2
    MEDIA_URL = f"https://{os.environ.get('R2_BUCKET_NAME')}.{os.environ.get('R2_CUSTOM_DOMAIN', 'r2.dev')}/"
    print("✅ Using Cloudflare R2 for media storage")
else:
    # Local storage (WARNING: Files will be lost on Render deploys!)
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    print("⚠️  WARNING: Using local media storage - files will be lost on deploy!")

# Logging for Production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
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
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'workplace_system': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Email Configuration for Production
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@school.com')

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Performance Settings
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get('DATA_UPLOAD_MAX_SIZE', '10485760'))
FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get('FILE_UPLOAD_MAX_SIZE', '10485760'))

# Render-specific optimizations
CONN_MAX_AGE = 600
ATOMIC_REQUESTS = True

# Error Tracking - Sentry
SENTRY_DSN = os.environ.get('SENTRY_DSN', '')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
                signals_spans=True,
            ),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            ),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment='production',
    )
    print("✅ Sentry error tracking enabled")
else:
    print("⚠️  Sentry not configured - production errors will not be tracked")

print("✅ Production settings loaded for Render deployment")