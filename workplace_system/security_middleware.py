"""
Security middleware for the application
"""
from django.utils.deprecation import MiddlewareMixin
from workplace_system.security import HeaderSecurityManager
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""
    
    def process_response(self, request, response):
        """Add security headers"""
        headers = HeaderSecurityManager.get_security_headers()
        
        for header, value in headers.items():
            response[header] = value
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """Log security-relevant requests"""
    
    def process_request(self, request):
        """Log incoming requests"""
        # Log failed authentication attempts
        if request.path.startswith('/accounts/login/') and request.method == 'POST':
            logger.info(f'Login attempt from {self.get_client_ip(request)}')
        
        return None
    
    def process_response(self, request, response):
        """Log response status"""
        # Log failed requests
        if response.status_code >= 400:
            logger.warning(
                f'{response.status_code} {request.method} {request.path} '
                f'from {self.get_client_ip(request)}'
            )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RateLimitMiddleware(MiddlewareMixin):
    """Rate limiting middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_counts = {}
        super().__init__(get_response)
    
    def process_request(self, request):
        """Check rate limits"""
        from django.core.cache import cache
        from django.http import HttpResponse
        
        client_ip = self.get_client_ip(request)
        cache_key = f'rate_limit_{client_ip}'
        
        # Get current count
        count = cache.get(cache_key, 0)
        
        # Check if exceeded
        if count > 100:  # 100 requests per minute
            logger.warning(f'Rate limit exceeded for {client_ip}')
            return HttpResponse('Rate limit exceeded', status=429)
        
        # Increment count
        cache.set(cache_key, count + 1, 60)  # 60 second window
        
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CSRFProtectionMiddleware(MiddlewareMixin):
    """Enhanced CSRF protection"""
    
    def process_request(self, request):
        """Validate CSRF token"""
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # Django's built-in CSRF middleware handles this
            pass
        
        return None


class XSSProtectionMiddleware(MiddlewareMixin):
    """XSS protection middleware"""
    
    def process_response(self, request, response):
        """Add XSS protection headers"""
        response['X-XSS-Protection'] = '1; mode=block'
        response['X-Content-Type-Options'] = 'nosniff'
        
        return response


class ClickjackingProtectionMiddleware(MiddlewareMixin):
    """Clickjacking protection middleware"""
    
    def process_response(self, request, response):
        """Add clickjacking protection headers"""
        response['X-Frame-Options'] = 'DENY'
        
        return response


class ContentSecurityPolicyMiddleware(MiddlewareMixin):
    """Content Security Policy middleware"""
    
    def process_response(self, request, response):
        """Add CSP headers"""
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response['Content-Security-Policy'] = csp
        
        return response


class SecurityAuditMiddleware(MiddlewareMixin):
    """Audit security-relevant events"""
    
    def process_request(self, request):
        """Audit incoming requests"""
        # Audit sensitive operations
        sensitive_paths = [
            '/accounts/login/',
            '/accounts/register/',
            '/admin/',
            '/api/',
        ]
        
        if any(request.path.startswith(path) for path in sensitive_paths):
            if request.method in ['POST', 'PUT', 'DELETE']:
                logger.info(
                    f'AUDIT: {request.method} {request.path} '
                    f'by {request.user} from {self.get_client_ip(request)}'
                )
        
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
