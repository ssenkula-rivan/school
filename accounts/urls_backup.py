from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Public School Registration (no login required)
    path('register-school/', views.public_school_registration, name='register_school'),
    
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('lockout/', TemplateView.as_view(template_name='accounts/lockout.html'), name='lockout'),
    
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
    
    # User Management
    path('manage-users/', views.manage_users, name='manage_users'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('change-role/<int:user_id>/', views.change_user_role, name='change_user_role'),
    
    # School Setup (for logged-in admins)
    path('setup/', views.school_setup_wizard, name='school_setup'),
    path('settings/school/', views.school_settings, name='school_settings'),
    
    # Data Import
    path('data-import/', views.data_import_dashboard, name='data_import'),
    path('data-import/students/', views.import_students, name='import_students'),
    path('data-import/employees/', views.import_employees, name='import_employees'),
    path('data-import/template/<str:data_type>/', views.download_template, name='download_template'),
    path('data-import/test-connection/', views.test_database_connection, name='test_db_connection'),
    path('data-import/from-database/', views.import_from_database, name='import_from_database'),
    
    # System Administrator
    path('sysadmin/', views.system_admin_login, name='sysadmin_login'),
    path('sysadmin/dashboard/', views.system_admin_dashboard, name='sysadmin_dashboard'),
    
    # Password Reset URLs - ADMIN ONLY
    path('admin-password-reset/', 
         views.AdminOnlyPasswordResetView.as_view(),
         name='admin_password_reset'),
    path('admin-password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/admin_password_reset_done.html'
         ), 
         name='admin_password_reset_done'),
    
    # Admin resets user password (sends email to user)
    path('admin/reset-user-password/<int:user_id>/', 
         views.admin_reset_user_password, 
         name='admin_reset_user_password'),
    
    # Admin directly sets user password (no email)
    path('admin/set-user-password/<int:user_id>/', 
         views.admin_set_user_password, 
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
    
    # Debug endpoint
    path('debug-config/', views.debug_config, name='debug_config'),
]
