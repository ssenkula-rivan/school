"""
Comprehensive System Security and Status Check
Provides complete system overview for security audit
"""
import os
import sys
import django
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.db import connection

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workplace_system.settings')
    django.setup()

@csrf_exempt
@require_GET
@login_required
def system_security_audit(request):
    """
    Complete system security and status audit
    Returns comprehensive system information for team access review
    """
    try:
        audit_data = {
            'timestamp': '2026-03-23T00:45:00Z',
            'audited_by': request.user.username,
            'system_info': {},
            'security_status': {},
            'database_info': {},
            'user_audit': {},
            'school_audit': {},
            'configuration_audit': {},
            'recommendations': []
        }
        
        # System Information
        audit_data['system_info'] = {
            'django_version': django.get_version(),
            'python_version': sys.version,
            'environment': 'Production' if not django.conf.settings.DEBUG else 'Development',
            'allowed_hosts': list(django.conf.settings.ALLOWED_HOSTS),
            'debug_mode': django.conf.settings.DEBUG,
            'secret_key_set': bool(django.conf.settings.SECRET_KEY),
            'database_engine': django.conf.settings.DATABASES['default']['ENGINE'],
        }
        
        # Security Status
        audit_data['security_status'] = {
            'csrf_enabled': 'django.middleware.csrf.CsrfViewMiddleware' in django.conf.settings.MIDDLEWARE,
            'auth_enabled': 'django.contrib.auth.middleware.AuthenticationMiddleware' in django.conf.settings.MIDDLEWARE,
            'axes_enabled': 'axes.middleware.AxesMiddleware' in django.conf.settings.MIDDLEWARE,
            'ssl_required': getattr(django.conf.settings, 'SECURE_SSL_REDIRECT', False),
            'hsts_enabled': getattr(django.conf.settings, 'SECURE_HSTS_SECONDS', 0) > 0,
            'session_secure': getattr(django.conf.settings, 'SESSION_COOKIE_SECURE', False),
        }
        
        # Database Information
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()[0]
            
            # Count all tables
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public';
            """)
            table_count = cursor.fetchone()[0]
            
            audit_data['database_info'] = {
                'database_version': db_version,
                'total_tables': table_count,
                'connection_secure': 'password' in str(django.conf.settings.DATABASES['default']),
            }
        
        # User Audit
        from django.contrib.auth.models import User
        from accounts.models import UserProfile
        
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        superusers = User.objects.filter(is_superuser=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        profiles_count = UserProfile.objects.count()
        
        audit_data['user_audit'] = {
            'total_users': total_users,
            'active_users': active_users,
            'superusers': superusers,
            'staff_users': staff_users,
            'with_profiles': profiles_count,
            'users_without_profiles': total_users - profiles_count,
            'last_login': User.objects.order_by('-last_login').first().last_login.isoformat() if User.objects.exists() else None,
        }
        
        # School Audit
        from core.models import School
        
        total_schools = School.objects.count()
        active_schools = School.objects.filter(is_active=True).count()
        
        audit_data['school_audit'] = {
            'total_schools': total_schools,
            'active_schools': active_schools,
            'inactive_schools': total_schools - active_schools,
            'schools_list': list(School.objects.values('id', 'name', 'code', 'is_active', 'created_at')),
        }
        
        # Configuration Audit
        audit_data['configuration_audit'] = {
            'middleware_count': len(django.conf.settings.MIDDLEWARE),
            'installed_apps_count': len(django.conf.settings.INSTALLED_APPS),
            'email_configured': bool(getattr(django.conf.settings, 'EMAIL_BACKEND', None)),
            'cache_configured': bool(django.conf.settings.CACHES),
            'logging_configured': bool(django.conf.settings.LOGGING),
            'staticfiles_configured': bool(django.conf.settings.STATIC_ROOT),
            'media_configured': bool(django.conf.settings.MEDIA_ROOT),
        }
        
        # Security Recommendations
        recommendations = []
        
        if django.conf.settings.DEBUG:
            recommendations.append("🔴 CRITICAL: DEBUG mode is enabled in production")
        
        if not django.conf.settings.SECRET_KEY:
            recommendations.append("🔴 CRITICAL: SECRET_KEY is not configured")
        
        if 'django.middleware.csrf.CsrfViewMiddleware' not in django.conf.settings.MIDDLEWARE:
            recommendations.append("🔴 CRITICAL: CSRF protection is disabled")
        
        if not getattr(django.conf.settings, 'SECURE_SSL_REDIRECT', False):
            recommendations.append("🟡 WARNING: SSL redirect is not enforced")
        
        if total_users > profiles_count:
            recommendations.append(f"🟡 WARNING: {total_users - profiles_count} users lack profiles")
        
        if superusers == 0:
            recommendations.append("🔴 CRITICAL: No superuser accounts exist")
        
        if total_schools == 0:
            recommendations.append("🔴 CRITICAL: No schools configured")
        
        audit_data['recommendations'] = recommendations
        
        return JsonResponse(audit_data, status=200)
        
    except Exception as e:
        error_data = {
            'error': str(e),
            'timestamp': '2026-03-23T00:45:00Z',
            'user': request.user.username if request.user.is_authenticated else 'Anonymous',
        }
        return JsonResponse(error_data, status=500)

# URL to add: path('security-audit/', system_security_audit, name='security_audit')
