"""
Management command to audit security settings
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from workplace_system.env_config import EnvironmentConfig


class Command(BaseCommand):
    help = 'Audit security settings'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('SECURITY AUDIT'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        checks = [
            self.check_debug_mode,
            self.check_secret_key,
            self.check_allowed_hosts,
            self.check_database,
            self.check_ssl,
            self.check_csrf,
            self.check_session,
            self.check_password_validation,
            self.check_logging,
        ]
        
        passed = 0
        failed = 0
        
        for check in checks:
            result = check()
            if result:
                passed += 1
            else:
                failed += 1
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS(f'Results: {passed} passed, {failed} failed'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
    
    def check_debug_mode(self):
        """Check DEBUG mode"""
        self.stdout.write('Checking DEBUG mode...', ending=' ')
        
        if settings.DEBUG:
            if EnvironmentConfig.IS_PRODUCTION:
                self.stdout.write(self.style.ERROR('❌ FAILED'))
                self.stdout.write(self.style.ERROR('  DEBUG=True in production is a CRITICAL SECURITY RISK'))
                return False
            else:
                self.stdout.write(self.style.WARNING('⚠️  WARNING'))
                self.stdout.write(self.style.WARNING('  DEBUG=True in development (acceptable)'))
                return True
        else:
            self.stdout.write(self.style.SUCCESS('✅ PASSED'))
            self.stdout.write(self.style.SUCCESS('  DEBUG=False'))
            return True
    
    def check_secret_key(self):
        """Check SECRET_KEY strength"""
        self.stdout.write('Checking SECRET_KEY strength...', ending=' ')
        
        secret_key = settings.SECRET_KEY
        
        if not secret_key:
            self.stdout.write(self.style.ERROR('❌ FAILED'))
            self.stdout.write(self.style.ERROR('  SECRET_KEY not set'))
            return False
        
        if len(secret_key) < 50:
            self.stdout.write(self.style.ERROR('❌ FAILED'))
            self.stdout.write(self.style.ERROR(f'  SECRET_KEY too weak ({len(secret_key)} chars, need 50+)'))
            return False
        
        if 'change' in secret_key.lower() or 'placeholder' in secret_key.lower():
            self.stdout.write(self.style.ERROR('❌ FAILED'))
            self.stdout.write(self.style.ERROR('  SECRET_KEY contains placeholder text'))
            return False
        
        self.stdout.write(self.style.SUCCESS('✅ PASSED'))
        self.stdout.write(self.style.SUCCESS(f'  SECRET_KEY is strong ({len(secret_key)} chars)'))
        return True
    
    def check_allowed_hosts(self):
        """Check ALLOWED_HOSTS"""
        self.stdout.write('Checking ALLOWED_HOSTS...', ending=' ')
        
        if not settings.ALLOWED_HOSTS:
            self.stdout.write(self.style.ERROR('❌ FAILED'))
            self.stdout.write(self.style.ERROR('  ALLOWED_HOSTS is empty'))
            return False
        
        if '*' in settings.ALLOWED_HOSTS:
            self.stdout.write(self.style.WARNING('⚠️  WARNING'))
            self.stdout.write(self.style.WARNING('  ALLOWED_HOSTS contains wildcard (*)'))
            return True
        
        self.stdout.write(self.style.SUCCESS('✅ PASSED'))
        self.stdout.write(self.style.SUCCESS(f'  ALLOWED_HOSTS: {", ".join(settings.ALLOWED_HOSTS)}'))
        return True
    
    def check_database(self):
        """Check database configuration"""
        self.stdout.write('Checking database...', ending=' ')
        
        db_engine = settings.DATABASES['default']['ENGINE']
        
        if 'sqlite' in db_engine and EnvironmentConfig.IS_PRODUCTION:
            self.stdout.write(self.style.ERROR('❌ FAILED'))
            self.stdout.write(self.style.ERROR('  SQLite in production is not recommended'))
            return False
        
        if 'postgresql' in db_engine:
            self.stdout.write(self.style.SUCCESS('✅ PASSED'))
            self.stdout.write(self.style.SUCCESS('  Using PostgreSQL'))
            return True
        
        self.stdout.write(self.style.WARNING('⚠️  WARNING'))
        self.stdout.write(self.style.WARNING(f'  Using {db_engine}'))
        return True
    
    def check_ssl(self):
        """Check SSL/TLS settings"""
        self.stdout.write('Checking SSL/TLS...', ending=' ')
        
        if EnvironmentConfig.IS_PRODUCTION:
            if not settings.SECURE_SSL_REDIRECT:
                self.stdout.write(self.style.ERROR('❌ FAILED'))
                self.stdout.write(self.style.ERROR('  SECURE_SSL_REDIRECT not enabled'))
                return False
            
            if not settings.SESSION_COOKIE_SECURE:
                self.stdout.write(self.style.ERROR('❌ FAILED'))
                self.stdout.write(self.style.ERROR('  SESSION_COOKIE_SECURE not enabled'))
                return False
            
            self.stdout.write(self.style.SUCCESS('✅ PASSED'))
            self.stdout.write(self.style.SUCCESS('  SSL/TLS properly configured'))
            return True
        else:
            self.stdout.write(self.style.WARNING('⚠️  WARNING'))
            self.stdout.write(self.style.WARNING('  SSL/TLS not required in development'))
            return True
    
    def check_csrf(self):
        """Check CSRF protection"""
        self.stdout.write('Checking CSRF protection...', ending=' ')
        
        if settings.CSRF_COOKIE_SECURE and settings.CSRF_COOKIE_HTTPONLY:
            self.stdout.write(self.style.SUCCESS('✅ PASSED'))
            self.stdout.write(self.style.SUCCESS('  CSRF protection enabled'))
            return True
        
        self.stdout.write(self.style.WARNING('⚠️  WARNING'))
        self.stdout.write(self.style.WARNING('  CSRF protection partially configured'))
        return True
    
    def check_session(self):
        """Check session security"""
        self.stdout.write('Checking session security...', ending=' ')
        
        if settings.SESSION_COOKIE_HTTPONLY:
            self.stdout.write(self.style.SUCCESS('✅ PASSED'))
            self.stdout.write(self.style.SUCCESS('  Session cookies are HTTPOnly'))
            return True
        
        self.stdout.write(self.style.ERROR('❌ FAILED'))
        self.stdout.write(self.style.ERROR('  SESSION_COOKIE_HTTPONLY not enabled'))
        return False
    
    def check_password_validation(self):
        """Check password validation"""
        self.stdout.write('Checking password validation...', ending=' ')
        
        validators = settings.AUTH_PASSWORD_VALIDATORS
        
        if len(validators) >= 3:
            self.stdout.write(self.style.SUCCESS('✅ PASSED'))
            self.stdout.write(self.style.SUCCESS(f'  {len(validators)} password validators enabled'))
            return True
        
        self.stdout.write(self.style.WARNING('⚠️  WARNING'))
        self.stdout.write(self.style.WARNING(f'  Only {len(validators)} password validators enabled'))
        return True
    
    def check_logging(self):
        """Check logging configuration"""
        self.stdout.write('Checking logging...', ending=' ')
        
        if 'django' in settings.LOGGING['loggers']:
            self.stdout.write(self.style.SUCCESS('✅ PASSED'))
            self.stdout.write(self.style.SUCCESS('  Logging properly configured'))
            return True
        
        self.stdout.write(self.style.WARNING('⚠️  WARNING'))
        self.stdout.write(self.style.WARNING('  Logging not configured'))
        return True
