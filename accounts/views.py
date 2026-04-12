import logging
from django.contrib.auth import views as auth_views, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from .models import UserProfile

logger = logging.getLogger(__name__)


def register(request):
    """Staff registration - available for multi-tenant system"""
    if request.method == 'POST':
        from .forms import UserRegistrationForm
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
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
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(request, f'{error}')
                        else:
                            messages.error(request, f'{field.upper()}: {error}')
    else:
        from .forms import UserRegistrationForm
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})




@login_required
def dashboard(request):
    """User dashboard - redirects employees to role-specific dashboards, admins to main dashboard"""
    try:
        user_profile = request.user.userprofile
    except:
        user_profile = UserProfile.objects.create(
            user=request.user,
            employee_id=f'EMP{request.user.id:04d}',
            role='admin' if request.user.is_superuser else 'staff',
            is_active_employee=True
        )
    
    role = user_profile.role
    
    # Admin and system_admin get the main dashboard with logged-in staff and statistics
    if role in ['admin', 'system_admin']:
        from core.models import Student, Grade
        from fees.models import FeeBalance
        from django.db.models import Sum, Count, Q
        
        # Get all currently logged-in staff from the same school
        logged_in_staff = UserProfile.objects.filter(
            school=user_profile.school,
            is_currently_logged_in=True,
            is_active_employee=True
        ).select_related('user').order_by('-last_login')
        
        # Student statistics
        total_students = Student.objects.filter(
            school=user_profile.school,
            status='active'
        ).count()
        
        # Students by gender
        male_students = Student.objects.filter(
            school=user_profile.school,
            status='active',
            gender='M'
        ).count()
        
        female_students = Student.objects.filter(
            school=user_profile.school,
            status='active',
            gender='F'
        ).count()
        
        # Students by grade
        students_by_grade = Student.objects.filter(
            school=user_profile.school,
            status='active'
        ).values('grade__name').annotate(
            count=Count('id')
        ).order_by('grade__name')
        
        # Scholarship students
        scholarship_students = Student.objects.filter(
            school=user_profile.school,
            status='active'
        ).exclude(scholarship_status='none').count()
        
        # Staff statistics
        total_staff = UserProfile.objects.filter(
            school=user_profile.school,
            is_active_employee=True
        ).count()
        
        # Fee statistics (if available)
        try:
            total_fees_owed = FeeBalance.objects.filter(
                student__school=user_profile.school,
                student__status='active'
            ).aggregate(total=Sum('balance'))['total'] or 0
            
            students_with_balance = FeeBalance.objects.filter(
                student__school=user_profile.school,
                student__status='active',
                balance__gt=0
            ).count()
        except:
            total_fees_owed = 0
            students_with_balance = 0
        
        context = {
            'user_profile': user_profile,
            'logged_in_staff': logged_in_staff,
            'total_logged_in': logged_in_staff.count(),
            
            # Student statistics
            'total_students': total_students,
            'male_students': male_students,
            'female_students': female_students,
            'students_by_grade': students_by_grade,
            'scholarship_students': scholarship_students,
            
            # Staff statistics
            'total_staff': total_staff,
            
            # Financial statistics
            'total_fees_owed': total_fees_owed,
            'students_with_balance': students_with_balance,
        }
        return render(request, 'dashboard/main.html', context)
    
    # Map employee roles to their specific dashboards
    role_dashboards = {
        'teacher': 'employees:teacher_dashboard',
        'director': 'employees:director_dashboard',
        'deputy_head_teacher': 'employees:director_dashboard',
        'dos': 'employees:dos_dashboard',
        'registrar': 'employees:registrar_dashboard',
        'hr_manager': 'employees:hr_dashboard',
        'head_of_class': 'employees:head_of_class_dashboard',
        'security': 'employees:security_dashboard',
        'receptionist': 'employees:receptionist_dashboard',
        'nurse': 'employees:nurse_dashboard',
        'accountant': 'accounting:dashboard',
        'bursar': 'fees:bursar_dashboard',
        'librarian': 'library:librarian_dashboard',
        'staff': 'employees:employee_dashboard',  # Generic staff dashboard
    }
    
    # Redirect employees to their role-specific dashboard
    if role in role_dashboards:
        return redirect(role_dashboards[role])
    
    # Fallback for parent, student, or undefined roles - show main dashboard
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'dashboard/main.html', context)


@login_required
def profile(request):
    """User profile management"""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        from .forms import UserProfileForm
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        from .forms import UserProfileForm
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'accounts/profile.html', {'form': form, 'user_profile': user_profile})


@login_required
def employee_list(request):
    """List all employees"""
    employees = UserProfile.objects.filter(is_active_employee=True).select_related('user', 'school')
    return render(request, 'accounts/employee_list.html', {'employees': employees})


@login_required
def manage_users(request):
    """Manage users - for HR, Director, and System Admin"""
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found')
        return redirect('accounts:dashboard')
    
    # Check permissions
    if user_profile.role not in ['director', 'hr', 'system_admin'] and not request.user.is_superuser:
        messages.error(request, 'Permission denied')
        return redirect('accounts:dashboard')
    
    school = user_profile.school
    users = User.objects.filter(userprofile__school=school).select_related('userprofile')
    
    context = {
        'users': users,
        'school': school,
    }
    return render(request, 'accounts/manage_users.html', context)


@login_required
def delete_user(request, user_id):
    """Delete a user account"""
    try:
        manager_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found')
        return redirect('accounts:dashboard')
    
    # Check permissions
    if manager_profile.role not in ['director', 'system_admin'] and not request.user.is_superuser:
        messages.error(request, 'Permission denied')
        return redirect('accounts:dashboard')
    
    try:
        user_to_delete = User.objects.get(id=user_id)
        user_profile = user_to_delete.userprofile
        
        # Don't allow deletion of superusers or yourself
        if user_to_delete.is_superuser or user_to_delete == request.user:
            messages.error(request, 'Cannot delete this user')
            return redirect('accounts:manage_users')
        
        if request.method == 'POST':
            username = user_to_delete.username
            user_to_delete.delete()
            messages.success(request, f'User {username} has been deleted')
            return redirect('accounts:manage_users')
        
        context = {
            'user_to_delete': user_to_delete,
            'user_profile': user_profile,
        }
        return render(request, 'accounts/delete_user_confirm.html', context)
        
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('accounts:manage_users')


@login_required
def change_user_role(request, user_id):
    """Change a user's role"""
    try:
        manager_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found')
        return redirect('accounts:dashboard')
    
    # Check permissions
    if manager_profile.role not in ['director', 'system_admin'] and not request.user.is_superuser:
        messages.error(request, 'Permission denied')
        return redirect('accounts:dashboard')
    
    try:
        target_user = User.objects.get(id=user_id)
        target_profile = target_user.userprofile
        
        # Don't allow role changes for superusers or yourself
        if target_user.is_superuser or target_user == request.user:
            messages.error(request, 'Cannot change role for this user')
            return redirect('accounts:manage_users')
        
        if request.method == 'POST':
            new_role = request.POST.get('role')
            if new_role in ['staff', 'teacher', 'hr', 'director']:
                target_profile.role = new_role
                target_profile.save()
                messages.success(request, f'Role updated for {target_user.username}')
            else:
                messages.error(request, 'Invalid role')
            return redirect('accounts:manage_users')
        
        context = {
            'target_user': target_user,
            'target_profile': target_profile,
            'roles': ['staff', 'teacher', 'hr', 'director'],
        }
        return render(request, 'accounts/change_user_role.html', context)
        
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('accounts:manage_users')


class CustomLoginView(auth_views.LoginView):
    """Custom login view that supports login by username or email."""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('accounts:dashboard')
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get(self, request, *args, **kwargs):
        """Display login page"""
        # Don't redirect to registration - let users login even if no schools exist
        # Superusers need to be able to login to create schools
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"CustomLoginView.get() called - path: {request.path}, user: {request.user}")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        username_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username_input:
            messages.error(request, 'Username or email is required.')
            return render(request, self.template_name, self.get_context_data())

        if not password:
            messages.error(request, 'Password is required.')
            return render(request, self.template_name, self.get_context_data())

        # Resolve username
        resolved_username = None
        try:
            if '@' in username_input:
                user_obj = User.objects.get(email__iexact=username_input)
                resolved_username = user_obj.username
            else:
                user_obj = User.objects.get(username__iexact=username_input)
                resolved_username = user_obj.username
        except User.DoesNotExist:
            messages.error(request, 'Invalid username or password. Please try again.')
            return render(request, self.template_name, self.get_context_data())
        except Exception as exc:
            messages.error(request, 'System error. Please try again later.')
            return render(request, self.template_name, self.get_context_data())

        # Authenticate
        user = authenticate(request, username=resolved_username, password=password)

        if user is None:
            messages.error(request, 'Invalid username or password. Please try again.')
            return render(request, self.template_name, self.get_context_data())

        if not user.is_active:
            messages.error(request, 'Your account is inactive. Please contact your school administrator.')
            return render(request, self.template_name, self.get_context_data())

        # Login succeeds
        login(request, user)
        logger.info("User '%s' logged in successfully.", user.username)
        
        # Ensure school admins always have is_staff=True
        try:
            profile = user.userprofile
            if profile.role in ['admin', 'system_admin', 'director']:
                if not user.is_staff:
                    user.is_staff = True
                    user.save(update_fields=['is_staff'])
                    logger.info(f"Auto-promoted {user.username} to is_staff=True")
        except Exception as e:
            logger.warning(f"Could not check admin role for {user.username}: {e}")
        
        # Track login in UserProfile
        try:
            from django.utils import timezone
            user_profile = user.userprofile
            user_profile.last_login = timezone.now()
            user_profile.is_currently_logged_in = True
            user_profile.login_ip = self.get_client_ip(request)
            user_profile.save(update_fields=['last_login', 'is_currently_logged_in', 'login_ip'])
        except Exception as e:
            logger.warning(f"Could not update login tracking for {user.username}: {e}")

        # Set school context
        self._set_school_session(request, user)

        # If no schools exist, inform the user but don't force redirect
        if request.session.get('no_schools_exist'):
            messages.success(request, f'Welcome {user.first_name or user.username}! You have been logged in successfully.')
            messages.info(request, 'No schools registered yet. You can register a school from the dashboard.')
        else:
            messages.success(
                request, 
                f'Welcome {user.first_name or user.username}! You have been logged in successfully.'
            )
        
        return redirect(self.get_success_url())

    @staticmethod
    def _set_school_session(request, user):
        """Determine which school this user belongs to and store it in the session."""
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
                    school = School.objects.filter(email_domain=domain, is_active=True).first()
                if school is None:
                    school = School.objects.filter(is_active=True).first()

            if school:
                request.session['school_id'] = school.id
                request.session['school_name'] = school.name
                logger.info("Session school set to '%s' (id=%s) for user '%s'", school.name, school.id, user.username)
            else:
                # No schools exist - set a temporary session flag
                request.session['no_schools_exist'] = True
                logger.warning("No schools exist for user '%s' - login proceeding without school context", user.username)

        except Exception as exc:
            logger.error("Failed to set school session for user '%s': %s", user.username, exc)
