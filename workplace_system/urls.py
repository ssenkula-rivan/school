from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect, HttpResponse, Http404
from django.core.cache import cache
from system_security_check import system_security_audit
from system_owner_panel import system_owner_dashboard, school_payment_api
from dev_mode_access import dev_login, simple_dashboard
from create_superuser import create_superuser_view
from debug_users import check_users, reset_and_create_admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

def health_check(request):
    """Health check endpoint - no DB queries"""
    return HttpResponse("ok", status=200)

def home_redirect(request):
    """Redirect to dev mode login"""
    return redirect('dev_login')

# Test error handlers in development
def test_404(request):
    raise Http404("Test 404 page")

def service_worker(request):
    """Serve service worker file"""
    from django.template.loader import render_to_string
    return HttpResponse(render_to_string('sw.js'), content_type='application/javascript')

def test_500(request):
    raise Exception("Test 500 page")

from show_errors import show_errors

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health'),
    path('errors/', show_errors, name='show_errors'),
    path('sw.js', service_worker, name='service_worker'),
    path('', home_redirect, name='home'),
    
    # Core apps - ONLY ESSENTIAL FOR FUNCTIONALITY
    # path('accounts/', include('accounts.urls')),  # DISABLED - broken auth
    
    # Dev Mode Access - Simple auto-login
    path('dev/login/', dev_login, name='dev_login'),
    path('dev/dashboard/', simple_dashboard, name='simple_dashboard'),
    
    # Emergency Superuser Creation
    path('create-superuser/', create_superuser_view, name='create_superuser'),
    
    # Database Diagnostic
    path('diagnose/', lambda request: HttpResponse(open('diagnose_login.py').read(), content_type='text/plain'), name='diagnose'),
    
    # Debug endpoints - check actual database state
    path('debug/users/', check_users, name='check_users'),
    path('debug/create-admin/', reset_and_create_admin, name='reset_and_create_admin'),
    
    # SYSTEM OWNER PANEL - SECRET ACCESS
    path('sys-admin-2024/', system_owner_dashboard, name='system_owner_dashboard'),
    path('sys-admin-2024/payment-api/<int:school_id>/', school_payment_api, name='school_payment_api'),
    
    # TEMPORARILY DISABLED TO FIX 500 ERRORS
    # path('core/', include('core.urls')),
    # path('subscriptions/', include('subscriptions.urls')),
    # path('employees/', include('employees.urls')),
    # path('fees/', include('fees.urls')),
    # path('academics/', include('academics.urls')),
    # path('library/', include('library.urls')),
    # path('inventory/', include('inventory.urls')),
    # path('reports/', include('reports.urls')),
    
    # Future API
    # path('api/v1/', include('api.urls', namespace='v1')),
]

# Test error pages in development
if settings.DEBUG:
    urlpatterns += [
        path('test-404/', test_404, name='test_404'),
        path('test-500/', test_500, name='test_500'),
    ]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)