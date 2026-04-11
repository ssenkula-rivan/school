from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from accounts.models import UserProfile
from accounts.decorators import admin_required


@login_required
@admin_required
def reset_employee_password(request, user_id):
    """Admin can reset employee password"""
    
    employee_user = get_object_or_404(User, id=user_id)
    
    try:
        employee_profile = employee_user.userprofile
        admin_profile = request.user.userprofile
        
        # Ensure admin can only reset passwords for users in their school
        if employee_profile.school != admin_profile.school:
            messages.error(request, 'You can only reset passwords for employees in your school.')
            return redirect('accounts:manage_users')
        
        # Prevent resetting other admin passwords
        if employee_profile.role == 'admin' and employee_user != request.user:
            messages.error(request, 'You cannot reset another admin password.')
            return redirect('accounts:manage_users')
        
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('accounts:manage_users')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if not new_password:
            messages.error(request, 'Password is required.')
        elif len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        elif new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        else:
            employee_user.set_password(new_password)
            employee_user.save()
            
            messages.success(
                request,
                f'Password reset successfully for {employee_user.get_full_name() or employee_user.username}. '
                f'New password: {new_password}'
            )
            return redirect('accounts:manage_users')
    
    context = {
        'employee': employee_user,
        'employee_profile': employee_profile,
    }
    return render(request, 'accounts/reset_employee_password.html', context)


@login_required
@admin_required
def manage_users(request):
    """List all users in the school for admin to manage"""
    
    try:
        admin_profile = request.user.userprofile
        school = admin_profile.school
        
        # Get all users in this school
        users = User.objects.filter(
            userprofile__school=school
        ).select_related('userprofile').order_by('username')
        
        context = {
            'users': users,
            'school': school,
        }
        return render(request, 'accounts/manage_users.html', context)
        
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('accounts:dashboard')
