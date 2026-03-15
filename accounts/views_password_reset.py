"""
Password reset views - Admin-controlled password management
- Regular users: Admin resets password for them
- Admin: Gets email reset link when they forget password
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from accounts.models import UserProfile
from core.middleware import get_current_school


class AdminOnlyPasswordResetView(PasswordResetView):
    """
    Password reset for admins only
    Regular users cannot self-serve password reset
    """
    template_name = 'accounts/admin_password_reset_form.html'
    success_url = '/accounts/admin-password-reset/done/'
    
    def get_queryset(self):
        """Only allow admins to reset their own password"""
        school = get_current_school()
        if not school:
            return User.objects.none()
        
        # Only admins can use this view
        return User.objects.filter(
            userprofile__role='admin',
            userprofile__school=school
        )


@login_required
@require_http_methods(["GET", "POST"])
def admin_reset_user_password(request, user_id):
    """
    Admin resets a user's password
    Only school admin can reset passwords for their school's users
    """
    school = get_current_school()
    if not school:
        messages.error(request, 'No school context')
        return redirect('accounts:login')
    
    # Check if current user is admin
    try:
        current_profile = request.user.userprofile
        if current_profile.role != 'admin' or current_profile.school != school:
            messages.error(request, 'Only school admin can reset passwords')
            return redirect('accounts:dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found')
        return redirect('accounts:login')
    
    # Get user to reset
    target_user = get_object_or_404(User, id=user_id)
    
    # Verify target user belongs to same school
    try:
        target_profile = target_user.userprofile
        if target_profile.school != school:
            messages.error(request, 'Cannot reset password for user from different school')
            return redirect('accounts:manage_users')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found')
        return redirect('accounts:manage_users')
    
    if request.method == 'POST':
        # Generate reset token
        token = default_token_generator.make_token(target_user)
        reset_url = f"{settings.SITE_URL}/accounts/reset/{target_user.pk}/{token}/"
        
        # Send email to user
        try:
            send_mail(
                subject='Password Reset Request',
                message=f'''
Hello {target_user.first_name},

Your school administrator has requested a password reset for your account.

Click the link below to reset your password:
{reset_url}

This link expires in 24 hours.

If you did not request this, please contact your school administrator.

Best regards,
{school.name}
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[target_user.email],
                fail_silently=False,
            )
            messages.success(request, f'Password reset link sent to {target_user.email}')
            return redirect('accounts:manage_users')
        except Exception as e:
            messages.error(request, f'Error sending email: {str(e)}')
            return redirect('accounts:manage_users')
    
    context = {
        'target_user': target_user,
        'school': school,
    }
    return render(request, 'accounts/admin_reset_user_password.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def admin_set_user_password(request, user_id):
    """
    Admin directly sets a user's password (without email)
    For emergency password resets
    """
    school = get_current_school()
    if not school:
        messages.error(request, 'No school context')
        return redirect('accounts:login')
    
    # Check if current user is admin
    try:
        current_profile = request.user.userprofile
        if current_profile.role != 'admin' or current_profile.school != school:
            messages.error(request, 'Only school admin can set passwords')
            return redirect('accounts:dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found')
        return redirect('accounts:login')
    
    # Get user
    target_user = get_object_or_404(User, id=user_id)
    
    # Verify target user belongs to same school
    try:
        target_profile = target_user.userprofile
        if target_profile.school != school:
            messages.error(request, 'Cannot set password for user from different school')
            return redirect('accounts:manage_users')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found')
        return redirect('accounts:manage_users')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not new_password or not confirm_password:
            messages.error(request, 'Both password fields are required')
            return redirect('accounts:manage_users')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('accounts:manage_users')
        
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters')
            return redirect('accounts:manage_users')
        
        # Set password
        target_user.set_password(new_password)
        target_user.save()
        
        # Force password reset on next login
        target_profile.force_password_reset = True
        target_profile.save()
        
        messages.success(request, f'Password set for {target_user.get_full_name()}')
        return redirect('accounts:manage_users')
    
    context = {
        'target_user': target_user,
        'school': school,
    }
    return render(request, 'accounts/admin_set_user_password.html', context)
