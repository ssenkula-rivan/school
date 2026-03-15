from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from accounts.school_config import SchoolConfiguration

def home_redirect(request):
    """Redirect to appropriate page based on school configuration"""
    config = SchoolConfiguration.get_config()
    if not config or not config.is_configured:
        # School not registered yet - go to public registration
        return redirect('accounts:register_school')
    elif not request.user.is_authenticated:
        # School registered but user not logged in
        return redirect('accounts:login')
    else:
        # User logged in - go to dashboard
        return redirect('accounts:dashboard')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    path('accounts/', include('accounts.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('employees/', include('employees.urls')),
    path('fees/', include('fees.urls')),
    path('reports/', include('reports.urls')),
    path('library/', include('library.urls')),
    path('core/', include('core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)