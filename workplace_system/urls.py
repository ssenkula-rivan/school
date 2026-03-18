from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.http import HttpResponse, Http404
from django.core.cache import cache

def health_check(request):
    """Health check endpoint - no DB queries"""
    return HttpResponse("ok", status=200)

def home_redirect(request):
    """Redirect to appropriate page - multi-tenant system"""
    # For multi-tenant system, always show school selection/registration
    if not request.user.is_authenticated:
        return redirect('accounts:register_school')
    else:
        # Authenticated users go to dashboard
        return redirect('accounts:dashboard')

# Test error handlers in development
def test_404(request):
    raise Http404("Test 404 page")

def test_500(request):
    raise Exception("Test 500 page")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health'),
    path('', home_redirect, name='home'),
    
    # Core apps
    path('accounts/', include('accounts.urls')),
    path('core/', include('core.urls')),
    
    # Feature apps
    path('subscriptions/', include('subscriptions.urls')),
    path('employees/', include('employees.urls')),
    path('fees/', include('fees.urls')),
    path('academics/', include('academics.urls')),
    path('library/', include('library.urls')),
    path('inventory/', include('inventory.urls')),
    path('reports/', include('reports.urls')),
    
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