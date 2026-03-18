from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from core.models import Department
from .models import UserProfile
from .forms import UserRegistrationForm, UserProfileForm # type: ignore
from .decorators import role_required, can_manage_employees

def register(request):
    """
    Staff registration - available for multi-tenant system
    Users can register staff for any school
    """
    # Remove single-school restriction for multi-tenant system
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Get the created profile to show employee ID
                profile = UserProfile.objects.get(user=user)
                username = form.cleaned_data.get('username')
                messages.success(
                    request, 
                    f'✅ Account created successfully! Your Employee ID is: {profile.employee_id}. Please login with username: {username}'
                )
                return redirect('accounts:login')
            except Exception as e:
                messages.error(request, f'❌ Error creating account: {str(e)}. Please try again.')
        else:
            # Display form errors
            if form.errors:
                error_messages = []
                for field, errors in form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            error_messages.append(f'❌ {error}')
                        else:
                            error_messages.append(f'❌ {field.upper()}: {error}')
                
                for error_msg in error_messages:
                    messages.error(request, error_msg)
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard(request):
    """Main dashboard view with role-based redirection"""
    try:
        # Get user profile
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        user_profile = UserProfile.objects.create(
            user=request.user,
            employee_id=f'EMP{request.user.id:04d}',
            role='admin' if request.user.is_superuser else 'staff',
            is_active_employee=True
        )
    
    # Check if user has school assigned
    if not user_profile.school and not request.user.is_superuser:
        # Try to assign user to a school
        from core.models import School
        school = School.objects.filter(is_active=True).first()
        if school:
            user_profile.school = school
            user_profile.save()
    
    # Redirect to role-specific dashboard
    role_dashboards = {
        'teacher': 'employees:teacher_dashboard',
        'director': 'employees:director_dashboard',
        'dos': 'employees:dos_dashboard',
        'registrar': 'employees:registrar_dashboard',
        'head_of_class': 'employees:head_of_class_dashboard',
        'security': 'employees:security_dashboard',
        'bursar': 'fees:bursar_dashboard',
        'accountant': 'fees:bursar_dashboard',
        'hr_manager': 'employees:hr_dashboard',
        'receptionist': 'employees:receptionist_dashboard',
        'librarian': 'library:librarian_dashboard',
        'nurse': 'employees:nurse_dashboard',
    }
    
    if user_profile.role in role_dashboards:
        return redirect(role_dashboards[user_profile.role])
    
    # Get dashboard statistics based on role
    context = {
        'user_profile': user_profile,
        'total_employees': User.objects.filter(is_active=True).count(),
        'total_departments': Department.objects.count(),
        'user_role': user_profile.role,
        'recent_activities': [],
    }
    
    # Add role-specific data
    if user_profile.can_manage_fees:
        from core.models import Student
        from fees.models import FeePayment
        context['total_students'] = Student.objects.filter(status='active').count()
        context['pending_payments'] = FeePayment.objects.filter(payment_status='pending').count()
    
    if user_profile.can_manage_employees:
        from employees.models import Employee, LeaveRequest
        context['active_employees'] = Employee.objects.filter(employment_status='active').count()
        context['pending_leaves'] = LeaveRequest.objects.filter(status='pending').count()
    
    return render(request, 'dashboard/main.html', context)

@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'accounts/profile.html', {'form': form, 'user_profile': user_profile})

@login_required
def employee_list(request):
    employees = UserProfile.objects.filter(is_active_employee=True).select_related('user', 'department')
    return render(request, 'accounts/employee_list.html', {'employees': employees})


@login_required
def manage_users(request):
    """Manage users - for HR, Director, and System Admin"""
    try:
        manager_profile = request.user.userprofile
    except:
        messages.error(request, 'Profile not found.')
        return redirect('accounts:dashboard')
    
    # Check if user has permission to manage
    if manager_profile.role not in ['hr_manager', 'director'] and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to manage users.')
        return redirect('accounts:dashboard')
    
    from accounts.permissions import get_manageable_users
    
    # Get users that this manager can manage
    manageable_users = get_manageable_users(manager_profile)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        manageable_users = manageable_users.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(employee_id__icontains=search_query)
        )
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(manageable_users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'manager_role': manager_profile.role,
        'is_sysadmin': request.user.is_superuser,
    }
    
    return render(request, 'accounts/manage_users.html', context)

@login_required
def delete_user(request, user_id):
    """Delete a user account"""
    try:
        manager_profile = request.user.userprofile
    except:
        messages.error(request, 'Profile not found.')
        return redirect('accounts:dashboard')
    
    from accounts.permissions import can_delete_user
    
    # Get target user
    target_user = get_object_or_404(User, id=user_id)
    
    try:
        target_profile = target_user.userprofile
    except:
        messages.error(request, 'Target user profile not found.')
        return redirect('accounts:manage_users')
    
    # Check permission
    if not can_delete_user(manager_profile, target_profile):
        messages.error(request, 'You do not have permission to delete this user.')
        return redirect('accounts:manage_users')
    
    # Prevent self-deletion
    if target_user.id == request.user.id:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('accounts:manage_users')
    
    if request.method == 'POST':
        username = target_user.username
        target_user.delete()
        messages.success(request, f'User {username} has been deleted successfully.')
        return redirect('accounts:manage_users')
    
    context = {
        'target_user': target_user,
        'target_profile': target_profile,
    }
    
    return render(request, 'accounts/delete_user_confirm.html', context)

@login_required
def change_user_role(request, user_id):
    """Change a user's role"""
    try:
        manager_profile = request.user.userprofile
    except:
        messages.error(request, 'Profile not found.')
        return redirect('accounts:dashboard')
    
    from accounts.permissions import can_change_role
    
    # Get target user
    target_user = get_object_or_404(User, id=user_id)
    
    try:
        target_profile = target_user.userprofile
    except:
        messages.error(request, 'Target user profile not found.')
        return redirect('accounts:manage_users')
    
    if request.method == 'POST':
        new_role = request.POST.get('role')
        
        # Check permission
        if not can_change_role(manager_profile, target_profile, new_role):
            messages.error(request, 'You do not have permission to change this user to that role.')
            return redirect('accounts:manage_users')
        
        # Update role
        target_profile.role = new_role
        target_profile.save()
        
        messages.success(request, f'User {target_user.username} role changed to {target_profile.get_role_display()}.')
        return redirect('accounts:manage_users')
    
    # Get available roles based on manager's permissions
    if request.user.is_superuser:
        available_roles = UserProfile.ROLE_CHOICES
    elif manager_profile.role == 'director':
        # Director cannot create new Directors
        available_roles = [r for r in UserProfile.ROLE_CHOICES if r[0] != 'director' or target_profile.role == 'director']
    elif manager_profile.role == 'hr_manager':
        # HR can only assign non-protected roles
        protected = ['admin', 'director', 'hr_manager']
        available_roles = [r for r in UserProfile.ROLE_CHOICES if r[0] not in protected]
    else:
        available_roles = []
    
    context = {
        'target_user': target_user,
        'target_profile': target_profile,
        'available_roles': available_roles,
    }
    
    return render(request, 'accounts/change_user_role.html', context)
