import logging
from django.contrib.auth import views as auth_views, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

logger = logging.getLogger(__name__)


def register(request):
    """Staff registration - available for multi-tenant system"""
    if request.method == 'POST':
        from .forms import UserRegistrationForm
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                from .models import UserProfile
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
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(request, f'❌ {error}')
                        else:
                            messages.error(request, f'❌ {field.upper()}: {error}')
    else:
        from .forms import UserRegistrationForm
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def public_school_registration(request):
    """Public school registration for multi-tenant setup"""
    if request.method == 'POST':
        from .forms import UserRegistrationForm
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                from .models import UserProfile
                profile = UserProfile.objects.get(user=user)
                username = form.cleaned_data.get('username')
                messages.success(
                    request, 
                    f'✅ School registered successfully! Admin username: {username}, Employee ID: {profile.employee_id}'
                )
                return redirect('accounts:login')
            except Exception as e:
                messages.error(request, f'❌ Error registering school: {str(e)}. Please try again.')
        else:
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(request, f'❌ {error}')
                        else:
                            messages.error(request, f'❌ {field.upper()}: {error}')
    else:
        from .forms import UserRegistrationForm
        form = UserRegistrationForm()
    
    return render(request, 'accounts/public_school_registration.html', {'form': form})


@login_required
def dashboard(request):
    """User dashboard"""
    try:
        user_profile = request.user.userprofile
    except:
        from .models import UserProfile
        user_profile = UserProfile.objects.create(
            user=request.user,
            employee_id=f'EMP{request.user.id:04d}',
            role='admin' if request.user.is_superuser else 'staff',
            is_active_employee=True
        )
    
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

    def get(self, request, *args, **kwargs):
        """Check if schools exist - redirect to registration if none"""
        try:
            from core.models import School
            school_count = School.objects.filter(is_active=True).count()
            
            if school_count == 0:
                return redirect('accounts:register_school')
        except Exception:
            pass
        
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        username_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username_input:
            messages.error(request, '❌ Username or email is required.')
            return render(request, self.template_name, self.get_context_data())

        if not password:
            messages.error(request, '❌ Password is required.')
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
            messages.error(request, '❌ System error. Please try again later.')
            return render(request, self.template_name, self.get_context_data())

        # Authenticate
        user = authenticate(request, username=resolved_username, password=password)

        if user is None:
            messages.error(request, 'Invalid username or password. Please try again.')
            return render(request, self.template_name, self.get_context_data())

        if not user.is_active:
            messages.error(request, '❌ Your account is inactive. Please contact your school administrator.')
            return render(request, self.template_name, self.get_context_data())

        # Login succeeds
        login(request, user)
        logger.info("User '%s' logged in successfully.", user.username)

        # Set school context
        self._set_school_session(request, user)

        messages.success(request, f'✅ Welcome {user.first_name or user.username}! You have been logged in successfully.')
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
                logger.warning("No active school found for user '%s' — session has no school context.", user.username)

        except Exception as exc:
            logger.error("Failed to set school session for user '%s': %s", user.username, exc)
