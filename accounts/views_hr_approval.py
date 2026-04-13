"""
HR Approval System for Employee Self-Registrations
Allows HR managers and admins to approve/reject pending employee accounts
"""
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import UserProfile
from accounts.decorators import role_required

logger = logging.getLogger(__name__)


@login_required
@role_required('admin', 'system_admin', 'director', 'hr_manager')
def pending_employee_approvals(request):
    """View all pending employee registrations for approval"""
    
    try:
        user_profile = request.user.userprofile
        school = user_profile.school
    except:
        messages.error(request, 'User profile not found')
        return redirect('accounts:dashboard')
    
    # Get all pending employees for this school
    pending_profiles = UserProfile.objects.filter(
        school=school,
        is_active_employee=False,
        user__is_active=False
    ).select_related('user', 'department', 'position').order_by('-user__date_joined')
    
    context = {
        'pending_profiles': pending_profiles,
        'school': school,
    }
    
    return render(request, 'accounts/hr_pending_approvals.html', context)


@login_required
@role_required('admin', 'system_admin', 'director', 'hr_manager')
def approve_employee(request, user_id):
    """Approve a pending employee registration"""
    
    if request.method != 'POST':
        return redirect('accounts:pending_approvals')
    
    try:
        user_profile = request.user.userprofile
        school = user_profile.school
        
        # Get the pending employee
        employee_user = get_object_or_404(User, id=user_id)
        employee_profile = employee_user.userprofile
        
        # Verify employee belongs to same school
        if employee_profile.school != school:
            messages.error(request, 'You can only approve employees from your school')
            return redirect('accounts:pending_approvals')
        
        # Activate the account
        employee_user.is_active = True
        employee_user.save()
        
        employee_profile.is_active_employee = True
        employee_profile.save()
        
        messages.success(
            request,
            f'Employee {employee_user.get_full_name()} ({employee_profile.employee_id}) has been approved and can now login.'
        )
        
        logger.info(
            f'Employee {employee_user.username} approved by {request.user.username} '
            f'for school {school.name}'
        )
        
    except Exception as e:
        logger.error(f'Error approving employee: {str(e)}')
        messages.error(request, f'Error approving employee: {str(e)}')
    
    return redirect('accounts:pending_approvals')


@login_required
@role_required('admin', 'system_admin', 'director', 'hr_manager')
def reject_employee(request, user_id):
    """Reject and delete a pending employee registration"""
    
    if request.method != 'POST':
        return redirect('accounts:pending_approvals')
    
    try:
        user_profile = request.user.userprofile
        school = user_profile.school
        
        # Get the pending employee
        employee_user = get_object_or_404(User, id=user_id)
        employee_profile = employee_user.userprofile
        
        # Verify employee belongs to same school
        if employee_profile.school != school:
            messages.error(request, 'You can only reject employees from your school')
            return redirect('accounts:pending_approvals')
        
        # Get details before deletion
        employee_name = employee_user.get_full_name()
        employee_id = employee_profile.employee_id
        
        # Delete the user (will cascade delete profile)
        employee_user.delete()
        
        messages.success(
            request,
            f'Employee registration for {employee_name} ({employee_id}) has been rejected and removed.'
        )
        
        logger.info(
            f'Employee {employee_name} rejected by {request.user.username} '
            f'for school {school.name}'
        )
        
    except Exception as e:
        logger.error(f'Error rejecting employee: {str(e)}')
        messages.error(request, f'Error rejecting employee: {str(e)}')
    
    return redirect('accounts:pending_approvals')


@login_required
@role_required('admin', 'system_admin', 'director', 'hr_manager')
def view_employee_details(request, user_id):
    """View detailed information about a pending employee"""
    
    try:
        user_profile = request.user.userprofile
        school = user_profile.school
        
        # Get the pending employee
        employee_user = get_object_or_404(User, id=user_id)
        employee_profile = employee_user.userprofile
        
        # Verify employee belongs to same school
        if employee_profile.school != school:
            messages.error(request, 'Access denied')
            return redirect('accounts:pending_approvals')
        
        context = {
            'employee_user': employee_user,
            'employee_profile': employee_profile,
            'school': school,
        }
        
        return render(request, 'accounts/hr_employee_details.html', context)
        
    except Exception as e:
        logger.error(f'Error viewing employee details: {str(e)}')
        messages.error(request, f'Error: {str(e)}')
        return redirect('accounts:pending_approvals')
