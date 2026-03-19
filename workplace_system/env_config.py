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
    
    @classmethod
    def get_environment(cls):
        return os.environ.get('ENVIRONMENT', 'development').lower()
    
    @classmethod
    def is_production(cls):
        env = cls.get_environment()
        return (
            env in ['production', 'prod'] or 
            os.environ.get('RENDER', '').lower() in ('true', '1', 'yes') or
            bool(os.environ.get('DYNO'))  # Heroku
        )
    
    @classmethod
    def is_development(cls):
        env = cls.get_environment()
        return env in ['development', 'dev', 'local'] and not cls.is_production()
    
    @classmethod
    def get_debug(cls):
        return os.environ.get('DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def get_secret_key(cls):
        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key or len(secret_key) < 50:
            # Generate a secure 60-character key for production
            import secrets
            secret_key = secrets.token_urlsafe(60)  # 60 characters, well above 50 requirement
            if cls.is_production():
                print(f"Generated secure SECRET_KEY (60 chars) for production")
            else:
                print(f"Generated SECRET_KEY for development")
        return secret_key
    
    @classmethod
    def get_allowed_hosts(cls):
        return [h.strip() for h in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')]
    
    @classmethod
    def get_database_url(cls):
        return os.environ.get('DATABASE_URL', '').strip()
    
    @classmethod
    def get_db_engine(cls):
        url = cls.get_database_url()
        return 'django.db.backends.sqlite3' if url.startswith('sqlite') else 'django.db.backends.postgresql'
    
    @classmethod
    def get_email_backend(cls):
        # SAFE DEFAULT: Console backend to prevent accidental emails
        return os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
    
    @classmethod
    def get_log_level(cls):
        return os.environ.get('LOG_LEVEL', 'INFO' if cls.is_production() else 'DEBUG')
    
    @classmethod
    def validate(cls):
        """Validate critical environment settings - SAFE to call anytime"""
        errors = []
        warnings = []
        
        secret_key = cls.get_secret_key()
        
        # CRITICAL: SECRET_KEY must be set in production
        if cls.is_production():
            if not secret_key:
                errors.append('SECRET_KEY must be set as an environment variable in production!')
            elif len(secret_key) < 50:
                errors.append(f'SECRET_KEY is too weak ({len(secret_key)} chars). Must be 50+ characters in production.')
            elif 'change' in secret_key.lower() or 'placeholder' in secret_key.lower():
                errors.append('SECRET_KEY contains placeholder text in production!')
            elif secret_key.startswith('django-insecure-'):
                errors.append('SECRET_KEY is using Django development key in production!')
        else:
            # Development warnings only
            if not secret_key:
                warnings.append('SECRET_KEY is not set. Will auto-generate.')
            elif len(secret_key) < 50:
                warnings.append(f'SECRET_KEY is weak ({len(secret_key)} chars). Should be 50+ characters.')
        
        if cls.is_production():
            if cls.get_debug():
                errors.append('DEBUG=True in production is a CRITICAL SECURITY RISK!')
            
            database_url = cls.get_database_url()
            if not database_url:
                errors.append('DATABASE_URL must be set in production!')
            
            # Check settings module
            settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', '')
            if 'production' not in settings_module:
                warnings.append(f'DJANGO_SETTINGS_MODULE is "{settings_module}" - should contain "production"')
            
            email_user = os.environ.get('EMAIL_HOST_USER', '')
            email_pass = os.environ.get('EMAIL_HOST_PASSWORD', '')
            if not email_user or not email_pass:
                warnings.append('Email credentials not configured. Email sending will fail.')
            
            stripe_key = os.environ.get('STRIPE_SECRET_KEY', '')
            if not stripe_key:
                warnings.append('Stripe credentials not configured. Payment processing will fail.')
            
            # Check R2 storage
            r2_bucket = os.environ.get('R2_BUCKET_NAME', '')
            if not r2_bucket:
                warnings.append('R2 storage not configured. Media files will be lost on deploy!')
        
        if cls.is_development():
            if cls.get_debug():
                warnings.append('DEBUG=True in development. Remember to disable in production.')
            
            db_password = os.environ.get('DB_PASSWORD', '')
            if not db_password:
                warnings.append('DB_PASSWORD not set. PostgreSQL connection may fail.')
        
        return errors, warnings
    
    @classmethod
    def get_database_config(cls):
        """
        Get database configuration (PostgreSQL or SQLite).
        
        CRITICAL: Fails hard in production if DATABASE_URL missing
        """
        database_url = cls.get_database_url()
        
        try:
            if database_url:
                # Check if it's SQLite
                if database_url.startswith('sqlite'):
                    print(f"Using SQLite database from DATABASE_URL")
                    db_path = database_url.replace('sqlite:///', '')
                    if not db_path.startswith('/'):
                        db_path = BASE_DIR / db_path
                    return {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': str(db_path),
                    }
                
                print(f"Using DATABASE_URL for PostgreSQL configuration")
                config = dj_database_url.parse(
                    database_url,
                    conn_max_age=600,
                    conn_health_checks=True,  # CRITICAL: Prevent stale connections
                )
                if cls.is_production() and 'OPTIONS' not in config:
                    config['OPTIONS'] = {}
                if cls.is_production() and 'sslmode' not in config.get('OPTIONS', {}):
                    config['OPTIONS']['sslmode'] = 'require'
                
                print(f"Parsed database config: ENGINE={config.get('ENGINE')}, NAME={config.get('NAME')}")
                return config
        except Exception as e:
            print(f"Warning: Failed to parse DATABASE_URL: {e}")
        
        # CRITICAL: Fail hard in production if no DATABASE_URL
        if cls.is_production():
            raise ValueError(
                "CRITICAL: DATABASE_URL must be set in production. "
                "SQLite is not permitted on Render - data will be lost on deploy!"
            )
        
        # Development fallback
        db_password = os.environ.get('DB_PASSWORD', '')
        if db_password:
            print(f"Using explicit PostgreSQL configuration")
            return {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('DB_NAME', 'school_management_saas'),
                'USER': os.environ.get('DB_USER', ''),
                'PASSWORD': db_password,
                'HOST': os.environ.get('DB_HOST', 'localhost'),
                'PORT': os.environ.get('DB_PORT', '5432'),
                'CONN_MAX_AGE': 600,
                'ATOMIC_REQUESTS': True,
                'OPTIONS': {'connect_timeout': 10},
            }
        else:
            print(f"Using SQLite fallback for development")
            return {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
    
    @classmethod
    def get_cache_config(cls):
        """Get cache configuration dictionary"""
        use_redis = os.environ.get('USE_REDIS', 'False').lower() == 'true'
        if use_redis:
            redis_url = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1')
            return {
                'default': {
                    'BACKEND': 'django_redis.cache.RedisCache',
                    'LOCATION': redis_url,
                    'OPTIONS': {
                        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                        'CONNECTION_POOL_KWARGS': {
                            'max_connections': 50,
                            'retry_on_timeout': True,
                        },
                        'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                        'IGNORE_EXCEPTIONS': True,  # Don't crash if Redis is down
                    },
                    'TIMEOUT': 300,
                    'KEY_PREFIX': 'school_mgmt',
                }
            }
        else:
            return {
                'default': {
                    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                    'LOCATION': 'unique-snowflake',
                    'TIMEOUT': 300,
                    'OPTIONS': {
                        'MAX_ENTRIES': 1000
                    }
                }
            }
    
    @classmethod
    def get_storage_config(cls):
        """Get storage configuration for media files"""
        use_r2 = os.environ.get('USE_R2_STORAGE', 'False').lower() == 'true'
        
        if use_r2:
            return {
                "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
                "OPTIONS": {
                    "access_key": os.environ.get('R2_ACCESS_KEY_ID'),
                    "secret_key": os.environ.get('R2_SECRET_ACCESS_KEY'),
                    "bucket_name": os.environ.get('R2_BUCKET_NAME'),
                    "endpoint_url": os.environ.get('R2_ENDPOINT_URL'),
                    "region_name": "auto",
                    "file_overwrite": False,
                    "default_acl": None,
                    "signature_version": "s3v4",
                    "querystring_auth": True,
                    "querystring_expire": 3600,
                }
            }
        else:
            return {
                "BACKEND": "django.core.files.storage.FileSystemStorage",
            }
    
    @classmethod
    def get_sentry_dsn(cls):
        """Get Sentry DSN for error tracking"""
        return os.environ.get('SENTRY_DSN', '')
    @classmethod
    def print_config(cls):
        """Print current configuration (safe for logging)"""
        print("\n" + "="*60)
        print("ENVIRONMENT CONFIGURATION")
        print("="*60)
        print(f"Environment: {cls.get_environment().upper()}")
        print(f"DEBUG Mode: {cls.get_debug()}")
        database_url = cls.get_database_url()
        db_type = "SQLite" if database_url and database_url.startswith('sqlite') else "PostgreSQL" if database_url else "Not Set"
        print(f"Database: {db_type}")
        use_redis = os.environ.get('USE_REDIS', 'False').lower() == 'true'
        print(f"Cache: {'Redis' if use_redis else 'Local Memory'}")
        print(f"Email Backend: {cls.get_email_backend().split('.')[-1]}")
        print(f"Allowed Hosts: {', '.join(cls.get_allowed_hosts())}")
        print(f"SSL Redirect: {cls.is_production()}")
        use_r2 = os.environ.get('USE_R2_STORAGE', 'False').lower() == 'true'
        print(f"Storage: {'Cloudflare R2' if use_r2 else 'Local Filesystem'}")
        sentry_dsn = cls.get_sentry_dsn()
        print(f"Error Tracking: {'Sentry Enabled' if sentry_dsn else 'None'}")
        print("="*60 + "\n")


# REMOVED: Module-level validation that runs on every import
# This will be called from core/apps.py ready() method instead
