"""
Employee Self-Registration View
Allows employees to register themselves by first verifying their school
"""
import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from core.models import School
from employees.models import Department, Position
from accounts.models import UserProfile

logger = logging.getLogger(__name__)


def employee_self_registration(request):
    """
    Step 1: Employee enters school name to verify
    Step 2: Show registration form for that school
    """
    
    # Step 2: Show registration form if school is verified
    if request.method == 'POST' and 'school_id' in request.POST:
        # Check if we should show the form or process registration
        if request.POST.get('show_form') == '1':
            # Show the registration form
            try:
                school_id = request.POST.get('school_id')
                school = School.objects.get(id=school_id, is_active=True)
                return show_registration_form(request, school)
            except School.DoesNotExist:
                messages.error(request, 'School not found')
                return render(request, 'accounts/employee_registration_step1.html')
        else:
            # Process the registration
            return handle_employee_registration(request)
    
    # Step 1: School lookup
    if request.method == 'POST' and 'school_name' in request.POST:
        return verify_school(request)
    
    # Initial page - ask for school name
    return render(request, 'accounts/employee_registration_step1.html')


def verify_school(request):
    """Verify school exists and show registration form"""
    school_name = request.POST.get('school_name', '').strip()
    
    if not school_name:
        messages.error(request, 'Please enter your school name')
        return render(request, 'accounts/employee_registration_step1.html')
    
    # Search for school (case-insensitive, partial match)
    schools = School.objects.filter(
        Q(name__icontains=school_name) | Q(code__icontains=school_name),
        is_active=True
    )
    
    if not schools.exists():
        messages.error(
            request, 
            f'School "{school_name}" not found. Please check the spelling or contact your school administrator.'
        )
        return render(request, 'accounts/employee_registration_step1.html')
    
    if schools.count() > 1:
        # Multiple schools found - let user choose
        context = {
            'schools': schools,
            'search_term': school_name
        }
        return render(request, 'accounts/employee_registration_choose_school.html', context)
    
    # Single school found - show registration form
    school = schools.first()
    return show_registration_form(request, school)


def show_registration_form(request, school):
    """Show employee registration form for specific school"""
    
    # Get departments and positions for this school
    departments = Department.objects.filter(school=school)
    positions = Position.objects.filter(school=school)
    
    context = {
        'school': school,
        'departments': departments,
        'positions': positions,
        'role_choices': UserProfile.ROLE_CHOICES,
    }
    
    return render(request, 'accounts/employee_registration_step2.html', context)


def handle_employee_registration(request):
    """Process employee registration form"""
    try:
        # Get school
        school_id = request.POST.get('school_id')
        school = School.objects.get(id=school_id, is_active=True)
        
        # Get form data
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        
        department_id = request.POST.get('department')
        position_id = request.POST.get('position')
        role = request.POST.get('role')
        
        # Validation
        errors = []
        
        if not all([username, email, first_name, last_name, password1, password2, role]):
            errors.append('All required fields must be filled')
        
        if password1 != password2:
            errors.append('Passwords do not match')
        
        if len(password1) < 8:
            errors.append('Password must be at least 8 characters long')
        
        if User.objects.filter(username=username).exists():
            errors.append(f'Username "{username}" is already taken')
        
        if User.objects.filter(email=email).exists():
            errors.append(f'Email "{email}" is already registered')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return show_registration_form(request, school)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            is_active=False,  # Requires admin approval
            is_staff=False,
        )
        
        # Generate employee ID
        role_prefix = {
            'teacher': 'TCH',
            'accountant': 'ACC',
            'librarian': 'LIB',
            'security': 'SEC',
            'receptionist': 'REC',
            'nurse': 'NUR',
            'hr_manager': 'HRM',
            'bursar': 'BUR',
            'dos': 'DOS',
            'registrar': 'REG',
            'staff': 'STF',
        }.get(role, 'EMP')
        
        # Get last employee ID for this school
        last_profile = UserProfile.objects.filter(
            school=school,
            employee_id__startswith=role_prefix
        ).order_by('-employee_id').first()
        
        if last_profile:
            try:
                last_num = int(last_profile.employee_id[3:])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        employee_id = f"{role_prefix}{new_num:04d}"
        
        # Get department and position
        department = None
        position = None
        
        if department_id:
            try:
                department = Department.objects.get(id=department_id, school=school)
            except Department.DoesNotExist:
                pass
        
        if position_id:
            try:
                position = Position.objects.get(id=position_id, school=school)
            except Position.DoesNotExist:
                pass
        
        # Create user profile
        UserProfile.objects.create(
            user=user,
            school=school,
            employee_id=employee_id,
            role=role,
            phone=phone,
            department=department,
            position=position,
            is_active_employee=False,  # Requires admin approval
        )
        
        messages.success(
            request,
            f'Registration successful! Your Employee ID is: {employee_id}. '
            f'Your account is pending approval by the HR Manager or Administrator of {school.name}. '
            f'You will be notified once your account is approved and you can login.'
        )
        
        return redirect('accounts:login')
        
    except School.DoesNotExist:
        messages.error(request, 'School not found or inactive')
        return redirect('accounts:employee_register')
    
    except Exception as e:
        logger.error(f'Employee registration error: {str(e)}')
        messages.error(request, f'Registration failed: {str(e)}')
        return redirect('accounts:employee_register')
