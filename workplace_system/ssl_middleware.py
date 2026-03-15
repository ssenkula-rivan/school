"""
SSL/HTTPS Enforcement Middleware
"""
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import HttpResponsePermanentRedirect
import logging

logger = logging.getLogger(__name__)


class SSLEnforcementMiddleware(MiddlewareMixin):
    """Enforce HTTPS/SSL for all requests in production"""
    
    def process_request(self, request):
        """Redirect HTTP to HTTPS in production"""
        if not settings.DEBUG:
            # Check if request is already HTTPS
            if request.META.get('HTTP_X_FORWARDED_PROTO') == 'https':
                return None
            
            if request.is_secure():
                return None
            
            # Redirect to HTTPS
            url = request.build_absolute_uri(request.get_full_path())
            secure_url = url.replace('http://', 'https://', 1)
            
            logger.warning(f'Redirecting insecure request to HTTPS: {request.path}')
            return HttpResponsePermanentRedirect(secure_url)
        
        return None


class SecurityHeadersEnforcementMiddleware(MiddlewareMixin):
    """Enforce security headers on all responses"""
    
    def process_response(self, request, response):
        """Add security headers"""
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # XSS Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # HSTS (only in production)
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Content Security Policy
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
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response


class CookieSecurityMiddleware(MiddlewareMixin):
    """Enforce secure cookie settings"""
    
    def process_response(self, request, response):
        """Ensure cookies are secure"""
        
        if not settings.DEBUG:
            # Set secure flag on all cookies
            for cookie_name in response.cookies:
                response.cookies[cookie_name]['secure'] = True
                response.cookies[cookie_name]['httponly'] = True
                response.cookies[cookie_name]['samesite'] = 'Strict'
        
        return response


class HTTPSRedirectMiddleware(MiddlewareMixin):
    """Redirect all HTTP traffic to HTTPS"""
    
    def process_request(self, request):
        """Check for HTTPS"""
        if settings.DEBUG:
            return None
        
        # Check if behind proxy
        x_forwarded_proto = request.META.get('HTTP_X_FORWARDED_PROTO')
        if x_forwarded_proto:
            if x_forwarded_proto != 'https':
                url = request.build_absolute_uri(request.get_full_path())
                secure_url = url.replace('http://', 'https://', 1)
                logger.warning(f'Proxy redirect to HTTPS: {request.path}')
                return HttpResponsePermanentRedirect(secure_url)
        elif not request.is_secure():
            url = request.build_absolute_uri(request.get_full_path())
            secure_url = url.replace('http://', 'https://', 1)
            logger.warning(f'Direct redirect to HTTPS: {request.path}')
            return HttpResponsePermanentRedirect(secure_url)
        
        return None
