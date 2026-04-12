"""
Public School Registration - No login required
First step for new schools to register in the system
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.models import User
from .school_config import SchoolConfiguration, get_school_config
from .models import UserProfile
from core.models import School, AcademicYear, Grade
from django.utils import timezone
import re


def public_school_registration(request):
    """
    Public school registration - accessible without login
    Creates school configuration and admin account
    Multi-tenant: Allows multiple schools to register
    """
    
    # Uganda School System - School Levels
    SCHOOL_LEVELS = [
        ('baby_care', 'Baby Day Care'),
        ('nursery', 'Nursery School'),
        ('pre_primary', 'Pre-Primary School'),
        ('primary', 'Primary School (P1-P7)'),
        ('olevel', 'O-Level Only (S1-S4)'),
        ('alevel', 'A-Level Only (S5-S6)'),
        ('secondary', 'Full Secondary (S1-S6)'),
        ('technical', 'Technical School'),
        ('vocational', 'Vocational Training'),
        ('tertiary', 'Tertiary College'),
        ('teachers_college', 'Teachers\' College'),
        ('business_college', 'Business College'),
        ('health_college', 'Health Sciences College'),
        ('university', 'University'),
        ('combined', 'Combined School (Multiple Levels)'),
    ]
    
    # Institution Types - Ownership
    OWNERSHIP_TYPES = [
        ('government', 'Government'),
        ('private', 'Private'),
        ('religious', 'Religious'),
    ]
    
    # Institution Types - Accommodation
    ACCOMMODATION_TYPES = [
        ('boarding', 'Boarding School'),
        ('day', 'Day School'),
        ('mixed', 'Mixed (Day & Boarding)'),
    ]
    
    # Institution Types - Special Categories
    SPECIAL_CATEGORIES = [
        ('international', 'International'),
        ('vocational', 'Vocational/Technical'),
        ('special_needs', 'Special Needs'),
    ]
    
    # Get curriculum and timezone choices from School model
    from core.models import School
    CURRICULUM_CHOICES = School.CURRICULUM_CHOICES
    TIMEZONE_CHOICES = School.TIMEZONE_CHOICES
    
    context = {
        'school_levels': SCHOOL_LEVELS,
        'ownership_types': OWNERSHIP_TYPES,
        'accommodation_types': ACCOMMODATION_TYPES,
        'special_categories': SPECIAL_CATEGORIES,
        'curriculum_choices': CURRICULUM_CHOICES,
        'timezone_choices': TIMEZONE_CHOICES,
    }
    
    if request.method == 'POST':
        try:
            # --- Pull raw POST fields (matches your HTML template) ---
            school_name = request.POST.get('school_name', '').strip()
            school_motto = request.POST.get('school_motto', '').strip()
            address = request.POST.get('address', '').strip()
            phone = request.POST.get('phone', '').strip()
            email = request.POST.get('email', '').strip()
            website = request.POST.get('website', '').strip()
            
            admin_first = request.POST.get('admin_first_name', '').strip()
            admin_last = request.POST.get('admin_last_name', '').strip()
            admin_username = request.POST.get('admin_username', '').strip()
            admin_email = request.POST.get('admin_email', '').strip()
            admin_phone = request.POST.get('admin_phone', '').strip()
            admin_password = request.POST.get('admin_password', '')
            admin_confirm = request.POST.get('admin_password_confirm', '')
            
            school_levels = request.POST.getlist('school_level')
            ownership_types = request.POST.getlist('ownership_type')
            accommodation_types = request.POST.getlist('accommodation_type')
            special_categories = request.POST.getlist('special_category')
            
            # Get curriculum and timezone
            curriculum = request.POST.get('curriculum', 'uganda_primary')
            secondary_curriculum = request.POST.get('secondary_curriculum', '')
            timezone_choice = request.POST.get('timezone', 'Africa/Kampala')
            
            # --- Validate required fields ---
            errors = []
            if not school_name:
                errors.append('School name is required.')
            if not school_levels:
                errors.append('At least one school level is required.')
            if not address:
                errors.append('Address is required.')
            if not phone:
                errors.append('Phone number is required.')
            if not email:
                errors.append('School email is required.')
            if not admin_username:
                errors.append('Admin username is required.')
            if not admin_email:
                errors.append('Admin email is required.')
            if not admin_password:
                errors.append('Password is required.')
            if admin_password != admin_confirm:
                errors.append('Passwords do not match.')
            if len(admin_password) < 8:
                errors.append('Password must be at least 8 characters.')
            if User.objects.filter(username=admin_username).exists():
                errors.append(f'Username "{admin_username}" is already taken.')
            if School.objects.filter(name=school_name).exists():
                errors.append(f'School "{school_name}" already exists.')
            
            if errors:
                for error in errors:
                    messages.error(request, error)
                return render(request, 'accounts/public_school_registration.html', context)
            
            # --- Start transaction ---
            with transaction.atomic():
                # Generate unique school code from name
                school_code = re.sub(r'[^a-z0-9]', '', school_name.lower())[:15]
                
                # Ensure code is unique
                base_code = school_code
                counter = 1
                while School.objects.filter(code=school_code).exists():
                    school_code = f"{base_code}{counter}"
                    counter += 1
                
                # Extract email domain
                admin_email_domain = admin_email.split('@')[1] if '@' in admin_email else f"{school_code}.edu"
                school_email_domain = email.split('@')[1] if '@' in email else admin_email_domain
                email_domain = admin_email_domain
                
                # Determine primary school_type (use first selected or 'combined' if multiple)
                if len(school_levels) > 1:
                    school_type = 'combined'
                elif len(school_levels) == 1:
                    # Map to legacy school_type
                    level_mapping = {
                        'baby_care': 'nursery',
                        'nursery': 'nursery',
                        'pre_primary': 'nursery',
                        'primary': 'primary',
                        'olevel': 'secondary',
                        'alevel': 'secondary',
                        'secondary': 'secondary',
                        'technical': 'college',
                        'vocational': 'college',
                        'tertiary': 'college',
                        'teachers_college': 'college',
                        'business_college': 'college',
                        'health_college': 'college',
                        'university': 'university',
                        'combined': 'combined',
                    }
                    school_type = level_mapping.get(school_levels[0], 'primary')
                else:
                    school_type = 'primary'  # Default
                
                # Determine primary institution_type
                institution_type = ownership_types[0] if ownership_types else 'private'
                
                # --- Create School with all selections ---
                current_date = timezone.now().date()
                school = School.objects.create(
                    name=school_name,
                    code=school_code,
                    school_type=school_type,
                    institution_type=institution_type,
                    email=email,
                    email_domain=email_domain,
                    phone=phone,
                    address=address,
                    website=website,
                    is_active=True,
                    subscription_start=current_date,
                    subscription_end=current_date.replace(year=current_date.year + 1),
                    max_students=1000,
                    max_staff=100,
                    currency='UGX',
                    timezone=timezone_choice,
                    curriculum=curriculum,
                    secondary_curriculum=secondary_curriculum,
                    
                    # School Levels
                    has_baby_care='baby_care' in school_levels,
                    has_nursery='nursery' in school_levels,
                    has_pre_primary='pre_primary' in school_levels,
                    has_primary='primary' in school_levels,
                    has_olevel='olevel' in school_levels,
                    has_alevel='alevel' in school_levels,
                    has_secondary='secondary' in school_levels,
                    has_technical='technical' in school_levels,
                    has_vocational='vocational' in school_levels,
                    has_tertiary='tertiary' in school_levels,
                    has_teachers_college='teachers_college' in school_levels,
                    has_business_college='business_college' in school_levels,
                    has_health_college='health_college' in school_levels,
                    has_university='university' in school_levels,
                    has_combined='combined' in school_levels,
                    
                    # Ownership Types
                    is_government='government' in ownership_types,
                    is_private='private' in ownership_types,
                    is_religious='religious' in ownership_types,
                    
                    # Accommodation Types
                    has_boarding='boarding' in accommodation_types,
                    has_day='day' in accommodation_types,
                    has_mixed_accommodation='mixed' in accommodation_types,
                    
                    # Special Categories
                    is_international='international' in special_categories,
                    is_vocational_technical='vocational' in special_categories,
                    is_special_needs='special_needs' in special_categories,
                )
                
                # --- Create School Configuration ---
                try:
                    SchoolConfiguration.objects.create(
                        school_name=school_name,
                        school_type=school_type,
                        institution_type=institution_type,
                        school_motto=school_motto,
                        address=address,
                        phone=phone,
                        email=email,
                        website=website,
                        is_configured=True
                    )
                except Exception as config_error:
                    # SchoolConfiguration is optional, don't fail if it errors
                    logger = logging.getLogger(__name__)
                    logger.warning(f'SchoolConfiguration creation failed: {config_error}')
                
                # --- Create Admin User with hashed password ---
                admin_user = User.objects.create_user(
                    username=admin_username,
                    email=admin_email,
                    password=admin_password,  # create_user calls set_password internally
                    first_name=admin_first,
                    last_name=admin_last,
                    is_staff=True,  # Allow access to admin panel
                    is_active=True,
                )
                
                # --- Create UserProfile linked to school ---
                UserProfile.objects.create(
                    user=admin_user,
                    school=school,
                    employee_id=f'ADM{admin_user.id:04d}',
                    role='admin',
                    phone=admin_phone,
                    is_active_employee=True,
                )
                
                # --- Create Academic Year ---
                current_year = timezone.now().year
                academic_year_name = f"{current_year}/{current_year + 1}"
                
                AcademicYear.objects.create(
                    school=school,
                    name=academic_year_name,
                    start_date=current_date,
                    end_date=current_date.replace(year=current_date.year + 1),
                    is_current=True
                )
                
                # --- Create Default Grades ---
                create_default_grades_for_school(school, school_levels)
                
                # --- Create Default Departments ---
                try:
                    from django.core.management import call_command
                    from io import StringIO
                    output = StringIO()
                    call_command('create_default_departments', school_code=school.code, stdout=output)
                    logger = logging.getLogger(__name__)
                    logger.info(f'Created default departments for {school.code}')
                except Exception as dept_error:
                    logger = logging.getLogger(__name__)
                    logger.warning(f'Failed to create default departments: {dept_error}')
                
                # --- Create Default Positions ---
                try:
                    from django.core.management import call_command
                    from io import StringIO
                    output = StringIO()
                    call_command('create_default_positions', school_code=school.code, stdout=output)
                    logger = logging.getLogger(__name__)
                    logger.info(f'Created default positions for {school.code}')
                except Exception as pos_error:
                    logger = logging.getLogger(__name__)
                    logger.warning(f'Failed to create default positions: {pos_error}')
                
                messages.success(
                    request,
                    f'School "{school_name}" registered successfully. Login with username: {admin_username}'
                )
                
                # Auto-login the admin user
                from django.contrib.auth import login, authenticate
                auto_login_user = authenticate(request, username=admin_username, password=admin_password)
                if auto_login_user:
                    login(request, auto_login_user)
                    request.session['school_id'] = school.id
                    request.session['school_name'] = school.name
                    return redirect('accounts:dashboard')
                else:
                    return redirect('accounts:login')
                
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            error_trace = traceback.format_exc()
            logger.error(f'Registration error: {error_trace}')
            messages.error(request, f'Registration failed: {str(e)}. Please try again.')
            
            # Show specific error details
            if 'UNIQUE constraint' in str(e):
                messages.error(request, 'A school with this name or code already exists.')
            elif 'NOT NULL constraint' in str(e):
                messages.error(request, 'Missing required field. Please fill all required fields.')
            
            return render(request, 'accounts/public_school_registration.html', context)
    
    return render(request, 'accounts/public_school_registration.html', context)


def create_default_grades_for_school(school, school_levels):
    """Create default grades based on selected school levels for a specific school
    
    Args:
        school: School instance
        school_levels: List of selected school level codes (e.g., ['primary', 'secondary'])
    """
    
    # Map school level codes to grade configurations
    level_to_grades = {
        'baby_care': [
            ('Baby Care - Infants', 1),
            ('Baby Care - Toddlers', 2),
        ],
        'nursery': [
            ('Nursery - Baby Class', 3),
            ('Nursery - Middle Class', 4),
            ('Nursery - Top Class', 5),
        ],
        'pre_primary': [
            ('Pre-Primary 1', 6),
            ('Pre-Primary 2', 7),
        ],
        'primary': [
            ('Primary 1', 10),
            ('Primary 2', 11),
            ('Primary 3', 12),
            ('Primary 4', 13),
            ('Primary 5', 14),
            ('Primary 6', 15),
            ('Primary 7', 16),
        ],
        'olevel': [
            ('O-Level - Senior 1', 20),
            ('O-Level - Senior 2', 21),
            ('O-Level - Senior 3', 22),
            ('O-Level - Senior 4', 23),
        ],
        'alevel': [
            ('A-Level - Senior 5', 24),
            ('A-Level - Senior 6', 25),
        ],
        'secondary': [
            ('Secondary - Senior 1', 20),
            ('Secondary - Senior 2', 21),
            ('Secondary - Senior 3', 22),
            ('Secondary - Senior 4', 23),
            ('Secondary - Senior 5', 24),
            ('Secondary - Senior 6', 25),
        ],
        'technical': [
            ('Technical - Year 1', 30),
            ('Technical - Year 2', 31),
            ('Technical - Year 3', 32),
        ],
        'vocational': [
            ('Vocational - Year 1', 35),
            ('Vocational - Year 2', 36),
        ],
        'tertiary': [
            ('Tertiary - Year 1', 40),
            ('Tertiary - Year 2', 41),
            ('Tertiary - Year 3', 42),
        ],
        'teachers_college': [
            ('Teachers College - Year 1', 45),
            ('Teachers College - Year 2', 46),
            ('Teachers College - Year 3', 47),
        ],
        'business_college': [
            ('Business College - Year 1', 50),
            ('Business College - Year 2', 51),
            ('Business College - Year 3', 52),
        ],
        'health_college': [
            ('Health College - Year 1', 55),
            ('Health College - Year 2', 56),
            ('Health College - Year 3', 57),
        ],
        'university': [
            ('University - Year 1', 60),
            ('University - Year 2', 61),
            ('University - Year 3', 62),
            ('University - Year 4', 63),
            ('University - Year 5', 64),
        ],
        'combined': [
            ('Nursery - Baby', 1),
            ('Nursery - Middle', 2),
            ('Nursery - Top', 3),
            ('Primary 1', 10),
            ('Primary 2', 11),
            ('Primary 3', 12),
            ('Primary 4', 13),
            ('Primary 5', 14),
            ('Primary 6', 15),
            ('Primary 7', 16),
            ('Senior 1', 20),
            ('Senior 2', 21),
            ('Senior 3', 22),
            ('Senior 4', 23),
            ('Senior 5', 24),
            ('Senior 6', 25),
        ],
    }
    
    # If school_levels is a string (legacy), convert to list
    if isinstance(school_levels, str):
        school_levels = [school_levels]
    
    # Collect all grades to create
    all_grades = []
    created_levels = set()  # Track which levels we've added to avoid duplicates
    
    for level_code in school_levels:
        if level_code in level_to_grades and level_code not in created_levels:
            all_grades.extend(level_to_grades[level_code])
            created_levels.add(level_code)
    
    # If no grades found, use primary as default
    if not all_grades:
        all_grades = level_to_grades['primary']
    
    # Sort by level number to ensure proper ordering
    all_grades.sort(key=lambda x: x[1])
    
    # Create grades in database
    for grade_name, level in all_grades:
        try:
            Grade.objects.create(
                school=school,
                name=grade_name,
                level=level
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'Failed to create grade {grade_name} for school {school.code}: {e}')
