from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views_sysadmin import system_admin_login, system_admin_dashboard
from .views_login import CustomLoginView
from .views_setup import school_setup_wizard, school_settings
from .views_public_setup import public_school_registration
from .views_data_import import (
    data_import_dashboard, import_students, import_employees,
    download_template, test_database_connection, import_from_database
)
from .views_password_reset import (
    AdminOnlyPasswordResetView, admin_reset_user_password, admin_set_user_password
)

app_name = 'accounts'

urlpatterns = [
    # Public School Registration (no login required)
    path('register-school/', public_school_registration, name='register_school'),
    
    # School Setup (for logged-in admins)
    path('setup/', school_setup_wizard, name='school_setup'),
    path('settings/school/', school_settings, name='school_settings'),
    
    # Data Import
    path('data-import/', data_import_dashboard, name='data_import'),
    path('data-import/students/', import_students, name='import_students'),
    path('data-import/employees/', import_employees, name='import_employees'),
    path('data-import/template/<str:data_type>/', download_template, name='download_template'),
    path('data-import/test-connection/', test_database_connection, name='test_db_connection'),
    path('data-import/from-database/', import_from_database, name='import_from_database'),
    
    # Authentication URLs
    path('login/', CustomLoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('register/', views.register, name='register'),

    # System Administrator
    path('sysadmin/', system_admin_login, name='sysadmin_login'),
    path('sysadmin/dashboard/', system_admin_dashboard, name='sysadmin_dashboard'),

    # Password Reset URLs - ADMIN ONLY
    # Regular users cannot self-serve password reset
    # Only admins get email reset links
    path('admin-password-reset/', 
         AdminOnlyPasswordResetView.as_view(),
         name='admin_password_reset'),
    path('admin-password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/admin_password_reset_done.html'
         ), 
         name='admin_password_reset_done'),
    
    # Admin resets user password (sends email to user)
    path('admin/reset-user-password/<int:user_id>/', 
         admin_reset_user_password, 
         name='admin_reset_user_password'),
    
    # Admin directly sets user password (no email)
    path('admin/set-user-password/<int:user_id>/', 
         admin_set_user_password, 
         name='admin_set_user_password'),
    
    # Standard password reset confirm (for admins only)
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/reset/done/'
         ), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
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

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # User Management
    path('manage-users/', views.manage_users, name='manage_users'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('change-role/<int:user_id>/', views.change_user_role, name='change_user_role'),
]
