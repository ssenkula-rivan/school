"""
Environment Configuration Manager
Handles environment-specific settings and validation
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / '.env')


class EnvironmentConfig:
    """Centralized environment configuration with validation"""
    
    # Environment detection - Handle Render and other hosting platforms
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development').lower()
    # Detect production environment (Render sets ENVIRONMENT=production, but also check other indicators)
    IS_PRODUCTION = (
        ENVIRONMENT in ['production', 'prod'] or 
        os.environ.get('RENDER') == 'true' or  # Render indicator
        os.environ.get('DYNO')  # Heroku indicator
    )
    IS_DEVELOPMENT = ENVIRONMENT in ['development', 'dev', 'local'] and not IS_PRODUCTION
    IS_STAGING = ENVIRONMENT in ['staging', 'stage'] and not IS_PRODUCTION
    
    # Django Core Settings
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')]
    
    # Security Settings
    SECURE_SSL_REDIRECT = IS_PRODUCTION
    SESSION_COOKIE_SECURE = IS_PRODUCTION
    CSRF_COOKIE_SECURE = IS_PRODUCTION
    SECURE_HSTS_SECONDS = 31536000 if IS_PRODUCTION else 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = IS_PRODUCTION
    SECURE_HSTS_PRELOAD = IS_PRODUCTION
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Database Settings - Auto-detect based on DATABASE_URL
    DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
    
    # Auto-detect database engine from DATABASE_URL
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DB_ENGINE = 'django.db.backends.postgresql'
    elif DATABASE_URL and DATABASE_URL.startswith('sqlite://'):
        DB_ENGINE = 'django.db.backends.sqlite3'
    elif os.environ.get('USE_POSTGRES', 'False').lower() == 'true':
        DB_ENGINE = 'django.db.backends.postgresql'
    else:
        DB_ENGINE = 'django.db.backends.sqlite3'  # Default to SQLite for safety
    
    DB_NAME = os.environ.get('DB_NAME', 'school_management_saas')
    DB_USER = os.environ.get('DB_USER', '')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    
    # Cache Settings
    USE_REDIS = os.environ.get('USE_REDIS', 'False').lower() == 'true'
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1')
    
    # Email Settings
    EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
    EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() == 'true'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@school.com')
    
    # Payment Gateway
    PAYMENT_GATEWAY = os.environ.get('PAYMENT_GATEWAY', 'stripe')
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', '')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
    
    # Logging
    LOG_LEVEL = 'WARNING' if IS_PRODUCTION else 'DEBUG'
    
    @classmethod
    def validate(cls):
        """Validate critical environment settings"""
        errors = []
        warnings = []
        
        # Warnings only - don't block deployment
        if not cls.SECRET_KEY:
            warnings.append('SECRET_KEY is not set. Will auto-generate.')
        
        # Validate SECRET_KEY strength if provided
        if cls.SECRET_KEY:
            if len(cls.SECRET_KEY) < 50:
                warnings.append(f'SECRET_KEY is weak ({len(cls.SECRET_KEY)} chars). Should be 50+ characters.')
            
            if 'change' in cls.SECRET_KEY.lower() or 'placeholder' in cls.SECRET_KEY.lower():
                warnings.append('SECRET_KEY contains placeholder text.')
            
            if cls.SECRET_KEY.startswith('django-insecure-'):
                warnings.append('SECRET_KEY is using Django development key.')
        
        if cls.IS_PRODUCTION:
            # Production-specific checks
            if cls.DEBUG:
                errors.append('DEBUG=True in production is a CRITICAL SECURITY RISK!')
            
            # Don't require SECRET_KEY - it will be auto-generated
            if not cls.DB_PASSWORD:
                warnings.append('DB_PASSWORD not set. Will use SQLite fallback.')
            
            if not cls.EMAIL_HOST_USER or not cls.EMAIL_HOST_PASSWORD:
                warnings.append('Email credentials not configured. Email sending will fail.')
            
            if not cls.STRIPE_SECRET_KEY:
                warnings.append('Stripe credentials not configured. Payment processing will fail.')
        
        # Development warnings
        if cls.IS_DEVELOPMENT:
            if cls.DEBUG:
                warnings.append('DEBUG=True in development. Remember to disable in production.')
            
            if not cls.DB_PASSWORD:
                warnings.append('DB_PASSWORD not set. PostgreSQL connection may fail.')
        
        return errors, warnings
    
    @classmethod
    def get_database_config(cls):
        """
        Get database configuration with auto-detection.
        
        Priority:
        1. DATABASE_URL (Render/Heroku style)
        2. Individual DB_* settings
        3. SQLite fallback
        """
        if cls.DATABASE_URL:
            print(f"Using DATABASE_URL for database configuration")
            try:
                config = dj_database_url.parse(
                    cls.DATABASE_URL,
                    conn_max_age=600,
                )
                # Add SSL mode for production if not already in URL
                if cls.IS_PRODUCTION and 'OPTIONS' not in config:
                    config['OPTIONS'] = {}
                if cls.IS_PRODUCTION and 'sslmode' not in config.get('OPTIONS', {}):
                    config['OPTIONS']['sslmode'] = 'require'
                
                print(f"Parsed database config: ENGINE={config.get('ENGINE')}, NAME={config.get('NAME')}")
                return config
            except Exception as e:
                print(f"Error parsing DATABASE_URL: {e}")
                print("Falling back to SQLite")
                return cls._get_sqlite_config()

        # Use explicit settings if PostgreSQL
        if cls.DB_ENGINE == 'django.db.backends.postgresql':
            print(f"Using explicit PostgreSQL configuration")
            config = {
                'ENGINE': cls.DB_ENGINE,
                'NAME': cls.DB_NAME,
                'USER': cls.DB_USER,
                'PASSWORD': cls.DB_PASSWORD,
                'HOST': cls.DB_HOST,
                'PORT': cls.DB_PORT,
                'CONN_MAX_AGE': 600,
                'ATOMIC_REQUESTS': True,
                'OPTIONS': {
                    'connect_timeout': 10,
                },
            }
            print(f"Database config: ENGINE={config.get('ENGINE')}, NAME={config.get('NAME')}")
            return config
        
        # Default to SQLite
        return cls._get_sqlite_config()
    
    @classmethod
    def _get_sqlite_config(cls):
        """Get SQLite configuration"""
        print("Using SQLite fallback configuration")
        from pathlib import Path
        base_dir = Path(__file__).resolve().parent.parent
        return {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': base_dir / 'db.sqlite3',
            'ATOMIC_REQUESTS': True,
        }
    
    @classmethod
    def get_cache_config(cls):
        """Get cache configuration dictionary"""
        if cls.USE_REDIS:
            return {
                'default': {
                    'BACKEND': 'django_redis.cache.RedisCache',
                    'LOCATION': cls.REDIS_URL,
                    'OPTIONS': {
                        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                    }
                }
            }
        else:
            return {
                'default': {
                    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                    'LOCATION': 'unique-snowflake',
                }
            }
    
    @classmethod
    def print_config(cls):
        """Print current configuration (safe for logging)"""
        print("\n" + "="*60)
        print("ENVIRONMENT CONFIGURATION")
        print("="*60)
        print(f"Environment: {cls.ENVIRONMENT.upper()}")
        print(f"DEBUG Mode: {cls.DEBUG}")
        print(f"Database: PostgreSQL")
        print(f"Cache: {'Redis' if cls.USE_REDIS else 'Local Memory'}")
        print(f"Email Backend: {cls.EMAIL_BACKEND.split('.')[-1]}")
        print(f"Allowed Hosts: {', '.join(cls.ALLOWED_HOSTS)}")
        print(f"SSL Redirect: {cls.SECURE_SSL_REDIRECT}")
        print("="*60 + "\n")


# Validate on import
errors, warnings = EnvironmentConfig.validate()

if errors:
    print("\n" + "!"*60)
    print("CONFIGURATION ERRORS:")
    print("!"*60)
    for error in errors:
        print(f"❌ {error}")
    print("!"*60 + "\n")
    # Don't raise in production - let it try to run with fallbacks
    if not EnvironmentConfig.IS_PRODUCTION:
        raise ValueError("Configuration errors detected!")

if warnings:
    print("\n" + "⚠️ "*30)
    print("CONFIGURATION WARNINGS:")
    print("⚠️ "*30)
    for warning in warnings:
        print(f"⚠️  {warning}")
    print("⚠️ "*30 + "\n")
