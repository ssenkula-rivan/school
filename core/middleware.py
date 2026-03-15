"""
Multi-tenant middleware for school isolation - ENTERPRISE GRADE
"""
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from .models import School
from contextvars import ContextVar
import logging

logger = logging.getLogger(__name__)

# CRITICAL: Use ContextVar instead of threading.local for ASGI safety
# ContextVar is safe for async views, ASGI, and thread reuse
_current_school: ContextVar[School] = ContextVar('current_school', default=None)


def get_current_school():
    """
    Get the current school from context
    
    ASGI-SAFE: Uses ContextVar instead of threading.local
    
    Returns None if no school context exists
    """
    return _current_school.get()


def set_current_school(school):
    """
    Set the current school in context
    
    ASGI-SAFE: Uses ContextVar instead of threading.local
    """
    _current_school.set(school)


def clear_current_school():
    """
    Clear school from context
    
    ASGI-SAFE: Uses ContextVar instead of threading.local
    """
    _current_school.set(None)


class TenantMiddleware(MiddlewareMixin):
    """
    Automatically set request.school for multi-tenant isolation
    
    CRITICAL SECURITY:
    - Validates school exists and is active
    - Caches school lookups for performance
    - Prevents school_id manipulation
    - Single source of truth: subdomain OR session (not user profile)
    - Fails securely if school cannot be determined
    """
    
    # Paths that don't require school context
    EXEMPT_PATHS = (
        '/admin/',
        '/static/',
        '/media/',
        '/accounts/register/',
        '/accounts/register-school/',
        '/accounts/login/',
        '/accounts/logout/',
        '/accounts/password-reset/',
        '/accounts/reset/',
    )
    
    def process_request(self, request):
        # Skip exempt paths
        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            return None
        
        school = None
        school_source = None
        
        # PRIORITY 1: Subdomain (production)
        school, school_source = self._get_school_from_subdomain(request)
        
        # PRIORITY 2: Session (fallback for development)
        if not school:
            school, school_source = self._get_school_from_session(request)
        
        # PRIORITY 3: First active school (development only)
        if not school and self._is_development():
            school, school_source = self._get_default_school(request)
        
        # Set school context
        if school:
            # Validate school is active
            if not school.is_active:
                logger.warning(
                    f"Attempted access to inactive school: {school.code}",
                    extra={'school_id': school.id, 'user': request.user}
                )
                messages.error(request, 'School account is inactive')
                return redirect('accounts:login')
            
            # CRITICAL: Check subscription status (SaaS enforcement)
            if hasattr(school, 'subscription'):
                subscription = school.subscription
                
                # Block access if subscription expired
                if subscription.status == 'expired':
                    logger.warning(
                        f"Access blocked - subscription expired: {school.code}",
                        extra={'school_id': school.id, 'user': request.user}
                    )
                    messages.error(request, 'Your subscription has expired. Please renew to continue.')
                    # Allow access to subscription pages only
                    if not request.path.startswith('/subscriptions/'):
                        return redirect('subscriptions:renew')
                
                # Block access if subscription suspended
                elif subscription.status == 'suspended':
                    logger.warning(
                        f"Access blocked - subscription suspended: {school.code}",
                        extra={'school_id': school.id, 'user': request.user}
                    )
                    messages.error(request, 'Your subscription is suspended. Please contact support.')
                    if not request.path.startswith('/subscriptions/'):
                        return redirect('subscriptions:suspended')
                
                # Warn if trial ending soon
                elif subscription.is_trial and subscription.days_until_expiry <= 3:
                    messages.warning(
                        request,
                        f'Your trial expires in {subscription.days_until_expiry} days. '
                        f'Subscribe now to avoid interruption.'
                    )
            
            # Set in request and thread-local
            request.school = school
            request.school_source = school_source
            set_current_school(school)
            
            # Update session if needed
            if request.session.get('school_id') != school.id:
                request.session['school_id'] = school.id
            
            logger.debug(
                f"School context set: {school.code} (source: {school_source})",
                extra={'school_id': school.id, 'user': request.user}
            )
        else:
            # No school context - fail securely
            request.school = None
            set_current_school(None)
            
            # For authenticated users, this is an error
            if request.user.is_authenticated:
                logger.error(
                    "No school context for authenticated user",
                    extra={'user': request.user, 'path': request.path}
                )
                messages.error(request, 'No school context found')
                return redirect('accounts:login')
        
        return None
    
    def _get_school_from_subdomain(self, request):
        """
        Get school from subdomain with caching
        
        CRITICAL SECURITY: Caches only school_id, not full object
        Always re-fetches with is_active=True validation
        
        Returns: (school, source) or (None, None)
        """
        host = request.get_host().split(':')[0]
        parts = host.split('.')
        
        # Check if subdomain exists
        if len(parts) <= 2:
            return None, None
        
        subdomain = parts[0]
        
        # Skip www
        if subdomain == 'www':
            return None, None
        
        # Check cache first (5 minute TTL) - ONLY cache ID, not object
        cache_key = f'school_subdomain:{subdomain}'
        school_id = cache.get(cache_key)
        
        if school_id:
            # CRITICAL: Always re-fetch with is_active=True (fresh from DB)
            try:
                school = School.objects.get(id=school_id, is_active=True)
                return school, 'subdomain'
            except School.DoesNotExist:
                # School deactivated or deleted - invalidate cache
                cache.delete(cache_key)
                logger.warning(
                    f"Cached school {school_id} no longer active, cache invalidated",
                    extra={'subdomain': subdomain}
                )
                return None, None
        
        # Query database
        try:
            school = School.objects.get(code=subdomain, is_active=True)
            # Cache ONLY the ID, not the full object
            cache.set(cache_key, school.id, 300)
            return school, 'subdomain'
        except School.DoesNotExist:
            logger.warning(
                f"Invalid subdomain: {subdomain}",
                extra={'host': host}
            )
            return None, None
    
    def _get_school_from_session(self, request):
        """
        Get school from session with validation
        
        CRITICAL SECURITY: 
        - Caches only school_id, not full object
        - Always re-fetches with is_active=True validation
        - Validates school_id hasn't been tampered with
        
        Returns: (school, source) or (None, None)
        """
        school_id = request.session.get('school_id')
        
        if not school_id:
            return None, None
        
        # Validate school_id is integer
        try:
            school_id = int(school_id)
        except (TypeError, ValueError):
            logger.warning(
                f"Invalid school_id in session: {school_id}",
                extra={'user': request.user}
            )
            del request.session['school_id']
            return None, None
        
        # CRITICAL: Always fetch fresh from DB with is_active=True
        # Don't cache full object - security-related data must be fresh
        try:
            school = School.objects.get(id=school_id, is_active=True)
            return school, 'session'
        except School.DoesNotExist:
            logger.warning(
                f"School {school_id} not found or inactive",
                extra={'user': request.user}
            )
            del request.session['school_id']
            return None, None
    
    def _get_default_school(self, request):
        """
        Get first active school (DEVELOPMENT ONLY)
        
        Returns: (school, source) or (None, None)
        """
        from django.conf import settings
        
        if not settings.DEBUG:
            return None, None
        
        school = School.objects.filter(is_active=True).first()
        if school:
            logger.debug(
                f"Using default school: {school.code} (DEVELOPMENT ONLY)",
                extra={'school_id': school.id}
            )
            return school, 'default'
        
        return None, None
    
    def _is_development(self):
        """Check if running in development mode"""
        from django.conf import settings
        return settings.DEBUG
    
    def process_response(self, request, response):
        """Clean up thread-local storage"""
        clear_current_school()
        return response
    
    def process_exception(self, request, exception):
        """Clean up thread-local storage on exception"""
        clear_current_school()
        return None
