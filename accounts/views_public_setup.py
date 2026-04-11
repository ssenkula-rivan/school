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
    
    context = {
        'school_levels': SCHOOL_LEVELS,
        'ownership_types': OWNERSHIP_TYPES,
        'accommodation_types': ACCOMMODATION_TYPES,
        'special_categories': SPECIAL_CATEGORIES,
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
            
            # --- Validate required fields ---
            errors = []
            if not school_name:
                errors.append('School name is required.')
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
                    timezone='Africa/Kampala',
                    
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
                    is_staff=True,
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
                create_default_grades_for_school(school, school_type)
                
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


def create_default_grades_for_school(school, school_type):
    """Create default grades based on school type for a specific school"""
    
    grades_config = {
        'nursery': [
            ('Baby Class', 1),
            ('Middle Class', 2),
            ('Top Class', 3),
        ],
        'primary': [
            ('Primary 1', 1),
            ('Primary 2', 2),
            ('Primary 3', 3),
            ('Primary 4', 4),
            ('Primary 5', 5),
            ('Primary 6', 6),
            ('Primary 7', 7),
        ],
        'secondary': [
            ('Senior 1 / Form 1', 1),
            ('Senior 2 / Form 2', 2),
            ('Senior 3 / Form 3', 3),
            ('Senior 4 / Form 4', 4),
            ('Senior 5 / Form 5', 5),
            ('Senior 6 / Form 6', 6),
        ],
        'college': [
            ('Year 1', 1),
            ('Year 2', 2),
            ('Year 3', 3),
            ('Year 4', 4),
        ],
        'university': [
            ('Year 1', 1),
            ('Year 2', 2),
            ('Year 3', 3),
            ('Year 4', 4),
            ('Year 5', 5),
        ],
        'combined': [
            ('Nursery - Baby', 1),
            ('Nursery - Middle', 2),
            ('Nursery - Top', 3),
            ('Primary 1', 4),
            ('Primary 2', 5),
            ('Primary 3', 6),
            ('Primary 4', 7),
            ('Primary 5', 8),
            ('Primary 6', 9),
            ('Primary 7', 10),
            ('Senior 1', 11),
            ('Senior 2', 12),
            ('Senior 3', 13),
            ('Senior 4', 14),
            ('Senior 5', 15),
            ('Senior 6', 16),
        ],
    }
    
    grades = grades_config.get(school_type, grades_config['primary'])
    
    for grade_name, level in grades:
        Grade.objects.create(
            school=school,
            name=grade_name,
            level=level
        )
