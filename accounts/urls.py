from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from . import views
from .views_public_setup import public_school_registration
from .views_create_admin import create_school_admin
from .views_test_login import test_login_debug
from .views_reset_password import reset_employee_password, manage_users
from .views_logout import custom_logout
from .views_make_superuser import make_superuser_web

app_name = 'accounts'

urlpatterns = [
    # Public School Registration (no login required)
    path('register-school/', public_school_registration, name='register_school'),
    
    # Create Admin for Existing School (no login required)
    path('create-admin/', create_school_admin, name='create_admin'),
    
    # Make Superuser (for Render free tier - no shell access)
    path('make-superuser/', make_superuser_web, name='make_superuser_web'),
    
    # Debug login issues
    path('debug-login/', test_login_debug, name='debug_login'),
    
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('lockout/', TemplateView.as_view(template_name='accounts/lockout.html'), name='lockout'),
    
    # User Management (Admin only)
    path('manage-users/', manage_users, name='manage_users'),
    path('reset-password/<int:user_id>/', reset_employee_password, name='reset_employee_password'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('change-role/<int:user_id>/', views.change_user_role, name='change_user_role'),
    
    # User Management (Admin only)
    path('manage-users/', manage_users, name='manage_users'),
    path('reset-password/<int:user_id>/', reset_employee_password, name='reset_employee_password'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('change-role/<int:user_id>/', views.change_user_role, name='change_user_role'),
    
    # Password Reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Password Change URLs (for logged-in users)
    path('password-change/', 
        auth_views.PasswordChangeView.as_view(
            template_name='accounts/password_change_form.html',
            success_url='/accounts/password-change/done/'
        ), 
        name='password_change'),
    path('password-change/done/', 
        auth_views.PasswordChangeDoneView.as_view(
            template_name='accounts/password_change_done.html'
        ), 
        name='password_change_done'),
    
    # Profile URLs
    path('profile/', views.profile, name='profile'),
    path('employees/', views.employee_list, name='employee_list'),
]
