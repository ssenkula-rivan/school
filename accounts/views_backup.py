import logging
from django.contrib.auth import views as auth_views, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

logger = logging.getLogger(__name__)


def register(request):
    """
    Staff registration - available for multi-tenant system
    Users can register staff for any school
    """
    # Remove single-school restriction for multi-tenant system
    
    if request.method == 'POST':
        from .forms import UserRegistrationForm
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Get created profile to show employee ID
                from .models import UserProfile
                profile = UserProfile.objects.get(user=user)
                username = form.cleaned_data.get('username')
                messages.success(
                    request, 
                    f'Account created successfully! Your Employee ID is: {profile.employee_id}. Please login with username: {username}'
                )
                return redirect('accounts:login')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}. Please try again.')
        else:
            # Display form errors
            if form.errors:
                error_messages = []
                for field, errors in form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            error_messages.append(f'{error}')
                        else:
                            error_messages.append(f'{field.upper()}: {error}')
                
                for error_msg in error_messages:
                    messages.error(request, error_msg)
    else:
        from .forms import UserRegistrationForm
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(auth_views.LoginView):
    """
    Custom login view that supports login by username or email.
    Identifies user's school and stores it in the session.
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('accounts:dashboard')

    def get(self, request, *args, **kwargs):
        """Check if schools exist - redirect to registration if none"""
        try:
            from core.models import School
            school_count = School.objects.filter(is_active=True).count()
            
            if school_count == 0:
                # No schools exist - redirect to school registration
                return redirect('accounts:register_school')
        except Exception:
            # If we can't check schools, continue to login
            pass
        
        # Schools exist - show login page
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        username_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # ------------------------------------------------------------------ #
        # 1. Basic input validation
        # ------------------------------------------------------------------ #
        if not username_input:
            messages.error(request, 'Username or email is required.')
            return render(request, self.template_name, self.get_context_data())

        if not password:
            messages.error(request, 'Password is required.')
            return render(request, self.template_name, self.get_context_data())

        # ------------------------------------------------------------------ #
        # 2. System-administrator shortcut
        # ------------------------------------------------------------------ #
        if username_input.lower() in ['system administrator', 'sysadmin', 'system admin']:
            return redirect('accounts:sysadmin_login')

        # ------------------------------------------------------------------ #
        # 3. Resolve actual Django username (handles email login too)
        # ------------------------------------------------------------------ #
        resolved_username = None
        try:
            if '@' in username_input:
                # Caller supplied an email address
                user_obj = User.objects.get(email__iexact=username_input)
                resolved_username = user_obj.username
            else:
                # Caller supplied a username — verify it exists
                user_obj = User.objects.get(username__iexact=username_input)
                resolved_username = user_obj.username
        except User.DoesNotExist:
            logger.warning("Login failed: no user found for input='%s'", username_input)
            messages.error(request, 'Invalid username or password. Please try again.')
            return render(request, self.template_name, self.get_context_data())
        except User.MultipleObjectsReturned:
            logger.error("Multiple users share email '%s' — using first active", username_input)
            user_obj = User.objects.filter(
                email__iexact=username_input, is_active=True
            ).first()
            if user_obj is None:
                messages.error(request, 'Invalid username or password. Please try again.')
                return render(request, self.template_name, self.get_context_data())
            resolved_username = user_obj.username
        except Exception as exc:
            logger.error("Database error during user lookup for '%s': %s", username_input, exc)
            messages.error(request, 'System error. Please try again later.')
            return render(request, self.template_name, self.get_context_data())

        # ------------------------------------------------------------------ #
        # 4. Authenticate with Django (also runs Axes lockout check)
        # ------------------------------------------------------------------ #
        user = authenticate(request, username=resolved_username, password=password)

        if user is None:
            logger.warning(
                "Authentication failed for username='%s' (resolved from '%s')",
                resolved_username, username_input,
            )
            messages.error(request, 'Invalid username or password. Please try again.')
            return render(request, self.template_name, self.get_context_data())

        if not user.is_active:
            logger.warning("Inactive user attempted login: '%s'", resolved_username)
            messages.error(
                request,
                'Your account is inactive. Please contact your school administrator.',
            )
            return render(request, self.template_name, self.get_context_data())

        # ------------------------------------------------------------------ #
        # 5. Login succeeds — create session
        # ------------------------------------------------------------------ #
        login(request, user)
        logger.info("User '%s' logged in successfully.", user.username)

        # ------------------------------------------------------------------ #
        # 6. Attach school context to session
        # ------------------------------------------------------------------ #
        self._set_school_session(request, user)

        messages.success(
            request,
            f'Welcome {user.first_name or user.username}! You have been logged in successfully.',
        )
        return redirect(self.get_success_url())

    # ---------------------------------------------------------------------- #
    # Helpers
    # ---------------------------------------------------------------------- #

    @staticmethod
    def _set_school_session(request, user):
        """
        Determine which school this user belongs to and store it in the
        session so downstream views can apply per-school tenant isolation.
        """
        try:
            from core.models import School

            school = None

            if user.is_superuser:
                school = School.objects.filter(is_active=True).first()

            elif hasattr(user, 'userprofile') and user.userprofile.school:
                school = user.userprofile.school

            else:
                if user.email and '@' in user.email:
                    domain = user.email.split('@')[1]
                    school = School.objects.filter(
                        email_domain=domain, is_active=True
                    ).first()
                if school is None:
                    school = School.objects.filter(is_active=True).first()

            if school:
                request.session['school_id'] = school.id
                request.session['school_name'] = school.name
                logger.info(
                    "Session school set to '%s' (id=%s) for user '%s'",
                    school.name, school.id, user.username,
                )
            else:
                logger.warning(
                    "No active school found for user '%s' — session has no school context.",
                    user.username,
                )

        except Exception as exc:
            logger.error(
                "Failed to set school session for user '%s': %s",
                user.username, exc,
            )

@login_required
def dashboard(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(
            user=request.user,
            employee_id=f'EMP{request.user.id:04d}',
            role='admin' if request.user.is_superuser else 'staff',
            is_active_employee=True
        )
    
    if not user_profile.school and not request.user.is_superuser:
        from core.models import School
        school = School.objects.filter(is_active=True).first()
        if school:
            user_profile.school = school
            user_profile.save()
    
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
    
    context = {
        'user_profile': user_profile,
        'total_employees': User.objects.filter(is_active=True).count(),
        'total_departments': Department.objects.count(),
        'user_role': user_profile.role,
        'recent_activities': [],
    }
    
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
