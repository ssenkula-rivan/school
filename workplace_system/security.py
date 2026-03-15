"""
Security utilities for the application
"""
import secrets
import string
from django.core.management.utils import get_random_secret_key


class SecureKeyGenerator:
    """Generate cryptographically secure keys"""
    
    @staticmethod
    def generate_secret_key():
        """Generate a Django-compatible SECRET_KEY"""
        return get_random_secret_key()
    
    @staticmethod
    def generate_api_key(length=32):
        """Generate a secure API key"""
        alphabet = string.ascii_letters + string.digits + '-_'
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def generate_token(length=64):
        """Generate a secure random token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_password(length=16):
        """Generate a secure random password"""
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
        password = [
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.digits),
            secrets.choice('!@#$%^&*'),
        ]
        password += [secrets.choice(alphabet) for _ in range(length - 4)]
        return ''.join(secrets.SystemRandom().sample(password, len(password)))


class PasswordValidator:
    """Validate password strength"""
    
    MIN_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL = True
    
    @classmethod
    def validate(cls, password):
        """Validate password meets security requirements"""
        errors = []
        
        if len(password) < cls.MIN_LENGTH:
            errors.append(f'Password must be at least {cls.MIN_LENGTH} characters')
        
        if cls.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append('Password must contain uppercase letters')
        
        if cls.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append('Password must contain lowercase letters')
        
        if cls.REQUIRE_DIGITS and not any(c.isdigit() for c in password):
            errors.append('Password must contain digits')
        
        if cls.REQUIRE_SPECIAL and not any(c in '!@#$%^&*' for c in password):
            errors.append('Password must contain special characters (!@#$%^&*)')
        
        return len(errors) == 0, errors


class SessionSecurityManager:
    """Manage session security"""
    
    @staticmethod
    def get_session_config():
        """Get secure session configuration"""
        return {
            'SESSION_ENGINE': 'django.contrib.sessions.backends.db',
            'SESSION_COOKIE_AGE': 3600,  # 1 hour
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SECURE': True,
            'SESSION_COOKIE_SAMESITE': 'Strict',
            'SESSION_EXPIRE_AT_BROWSER_CLOSE': True,
        }


class CookieSecurityManager:
    """Manage cookie security"""
    
    @staticmethod
    def get_cookie_config():
        """Get secure cookie configuration"""
        return {
            'CSRF_COOKIE_SECURE': True,
            'CSRF_COOKIE_HTTPONLY': True,
            'CSRF_COOKIE_SAMESITE': 'Strict',
            'CSRF_COOKIE_AGE': 31449600,  # 1 year
        }


class HeaderSecurityManager:
    """Manage security headers"""
    
    @staticmethod
    def get_security_headers():
        """Get security headers for responses"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        }


class EncryptionManager:
    """Manage encryption for sensitive data"""
    
    @staticmethod
    def hash_sensitive_data(data):
        """Hash sensitive data"""
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def encrypt_field(value, key=None):
        """Encrypt a field value"""
        from cryptography.fernet import Fernet
        if not key:
            from django.conf import settings
            key = settings.SECRET_KEY.encode()[:32].ljust(32, b'0')
        
        cipher = Fernet(key)
        return cipher.encrypt(value.encode()).decode()
    
    @staticmethod
    def decrypt_field(encrypted_value, key=None):
        """Decrypt a field value"""
        from cryptography.fernet import Fernet
        if not key:
            from django.conf import settings
            key = settings.SECRET_KEY.encode()[:32].ljust(32, b'0')
        
        cipher = Fernet(key)
        return cipher.decrypt(encrypted_value.encode()).decode()
