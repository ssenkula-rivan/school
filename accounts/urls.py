from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from . import views
from .views_public_setup import public_school_registration

app_name = 'accounts'

urlpatterns = [
    # Public School Registration (no login required)
    path('register-school/', public_school_registration, name='register_school'),
    
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
]
