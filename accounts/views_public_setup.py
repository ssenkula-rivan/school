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
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                school_name = request.POST.get('school_name')
                
                # Get all selected school levels
                school_levels = request.POST.getlist('school_level')
                
                # Get all selected ownership types
                ownership_types = request.POST.getlist('ownership_type')
                
                # Get all selected accommodation types
                accommodation_types = request.POST.getlist('accommodation_type')
                
                # Get all selected special categories
                special_categories = request.POST.getlist('special_category')
                
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
                
                # Determine primary institution_type (use first selected)
                if ownership_types:
                    institution_type = ownership_types[0]
                else:
                    institution_type = 'private'  # Default
                
                # Generate unique school code from name
                import re
                school_code = re.sub(r'[^a-z0-9]', '', school_name.lower())[:15]
                
                # Ensure code is unique
                from core.models import School
                base_code = school_code
                counter = 1
                while School.objects.filter(code=school_code).exists():
                    school_code = f"{base_code}{counter}"
                    counter += 1
                
                # Extract email domain from admin email to match school
                admin_email = request.POST.get('admin_email')
                admin_email_domain = admin_email.split('@')[1] if '@' in admin_email else f"{school_code}.edu"
                
                # Extract email domain from school email
                school_email = request.POST.get('email')
                school_email_domain = school_email.split('@')[1] if '@' in school_email else admin_email_domain
                
                # Use admin email domain for school domain matching
                email_domain = admin_email_domain
                
                # Step 1: Create School with all selections
                current_date = timezone.now().date()
                school = School.objects.create(
                    name=school_name,
                    code=school_code,
                    school_type=school_type,
                    institution_type=institution_type,
                    email=school_email,
                    email_domain=email_domain,
                    phone=request.POST.get('phone'),
                    address=request.POST.get('address'),
                    website=request.POST.get('website', ''),
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
                
                # Step 2: Create School Configuration (for feature flags)
                school_config = SchoolConfiguration.objects.create(
                    school_name=school_name,
                    school_type=school_type,
                    institution_type=institution_type,
                    school_motto=request.POST.get('school_motto', ''),
                    address=request.POST.get('address'),
                    phone=request.POST.get('phone'),
                    email=request.POST.get('email'),
                    website=request.POST.get('website', ''),
                    is_configured=True
                )
                
                # Step 3: Create Admin User
                admin_username = request.POST.get('admin_username')
                admin_email = request.POST.get('admin_email')
                admin_password = request.POST.get('admin_password')
                admin_first_name = request.POST.get('admin_first_name')
                admin_last_name = request.POST.get('admin_last_name')
                
                # Check if school name already exists for this school type
                if School.objects.filter(name=school_name, school_type=school_type).exists():
                    messages.error(request, f'A school named "{school_name}" of type "{school_type}" already exists. Please choose a different name or contact support.')
                    return render(request, 'accounts/public_school_registration.html', {
                        'school_levels': SCHOOL_LEVELS,
                        'ownership_types': OWNERSHIP_TYPES,
                        'accommodation_types': ACCOMMODATION_TYPES,
                        'special_categories': SPECIAL_CATEGORIES,
                    })
                
                # Check if admin username already exists
                if User.objects.filter(username=admin_username).exists():
                    messages.error(request, 'Username already exists. Please choose another.')
                    return render(request, 'accounts/public_school_registration.html', {
                        'school_levels': SCHOOL_LEVELS,
                        'ownership_types': OWNERSHIP_TYPES,
                        'accommodation_types': ACCOMMODATION_TYPES,
                        'special_categories': SPECIAL_CATEGORIES,
                    })
                
                # Create admin user (regular user, not superuser - for school isolation)
                admin_user = User.objects.create_user(
                    username=admin_username,
                    email=admin_email,
                    password=admin_password,
                    first_name=admin_first_name,
                    last_name=admin_last_name,
                    is_staff=True  # Can access admin panel, but only for their school
                )
                
                # Create admin profile linked to school
                try:
                    UserProfile.objects.create(
                        user=admin_user,
                        school=school,  # Link admin to their specific school
                        employee_id='ADMIN001',
                        role='admin',
                        phone=request.POST.get('admin_phone', ''),
                        is_active_employee=True
                    )
                    print(f"✅ UserProfile created for admin: {admin_username}")
                except Exception as profile_error:
                    print(f"❌ UserProfile creation failed: {profile_error}")
                    # Delete the user if profile creation fails
                    admin_user.delete()
                    raise Exception(f"Failed to create user profile: {profile_error}")
                
                # Step 4: Create Academic Year
                current_year = timezone.now().year
                academic_year_name = f"{current_year}/{current_year + 1}"
                
                AcademicYear.objects.create(
                    school=school,
                    name=academic_year_name,
                    start_date=current_date,
                    end_date=current_date.replace(year=current_date.year + 1),
                    is_current=True
                )
                
                # Step 5: Create Default Grades based on school type
                create_default_grades_for_school(school, school_type)
                
                messages.success(
                    request, 
                    f'{school_name} has been registered successfully! '
                    f'Logging you in automatically with username: {admin_username}'
                )
                
                # Auto-login the admin user after registration
                from django.contrib.auth import login, authenticate
                auto_login_user = authenticate(request, username=admin_username, password=admin_password)
                if auto_login_user:
                    login(request, auto_login_user)
                    
                    # Set school context
                    request.session['school_id'] = school.id
                    request.session['school_name'] = school.name
                    
                    return redirect('accounts:dashboard')
                else:
                    # Fallback to login page if auto-login fails
                    return redirect('accounts:login')
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Registration error: {error_details}')
            messages.error(request, f'Registration failed: {str(e)}')
    
    context = {
        'school_levels': SCHOOL_LEVELS,
        'ownership_types': OWNERSHIP_TYPES,
        'accommodation_types': ACCOMMODATION_TYPES,
        'special_categories': SPECIAL_CATEGORIES,
    }
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


def create_default_grades(school_type):
    """Create default grades based on school type (deprecated - use create_default_grades_for_school)"""
    
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
        Grade.objects.get_or_create(
            name=grade_name,
            defaults={'level': level}
        )



def extract_category_specific_data(post_data, school_type):
    """
    Extract category-specific data based on school type
    Returns a dictionary with relevant fields for the selected school type
    """
    category_data = {}
    
    if school_type == 'nursery':
        category_data = {
            'age_range': post_data.get('nursery_age_range', ''),
            'number_of_classes': post_data.get('nursery_classes', ''),
            'special_programs': post_data.get('nursery_programs', ''),
        }
    
    elif school_type == 'primary':
        category_data = {
            'grade_levels': post_data.get('primary_grades', ''),
            'curriculum': post_data.get('primary_curriculum', ''),
            'activities': post_data.get('primary_activities', ''),
        }
    
    elif school_type == 'secondary':
        category_data = {
            'has_olevel': post_data.get('secondary_olevel') == '1',
            'has_alevel': post_data.get('secondary_alevel') == '1',
            'curriculum': post_data.get('secondary_curriculum', ''),
            'streams': post_data.get('secondary_streams', ''),
        }
    
    elif school_type == 'college':
        category_data = {
            'has_diploma': post_data.get('college_diploma') == '1',
            'has_certificate': post_data.get('college_certificate') == '1',
            'has_vocational': post_data.get('college_vocational') == '1',
            'program_duration': post_data.get('college_duration', ''),
            'departments': post_data.get('college_departments', ''),
        }
    
    elif school_type == 'university':
        category_data = {
            'number_of_faculties': post_data.get('university_faculties', ''),
            'number_of_departments': post_data.get('university_departments', ''),
            'has_undergraduate': post_data.get('university_undergraduate') == '1',
            'has_postgraduate': post_data.get('university_postgraduate') == '1',
            'has_phd': post_data.get('university_phd') == '1',
            'academic_system': post_data.get('university_system', ''),
            'faculty_names': post_data.get('university_faculty_names', ''),
        }
    
    elif school_type == 'combined':
        category_data = {
            'has_nursery': post_data.get('combined_nursery') == '1',
            'has_primary': post_data.get('combined_primary') == '1',
            'has_secondary': post_data.get('combined_secondary') == '1',
            'grade_range': post_data.get('combined_grade_range', ''),
        }
    
    # Remove empty values
    return {k: v for k, v in category_data.items() if v}
