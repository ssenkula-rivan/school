"""
School Setup Wizard Views
First-time configuration for the school system
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from .school_config import SchoolConfiguration, get_school_config
from fees.models import AcademicYear, Grade
from django.utils import timezone


def is_superuser(user):
    return user.is_superuser


@login_required
@user_passes_test(is_superuser)
def school_setup_wizard(request):
    """Initial school setup wizard"""
    
    # Check if already configured
    config = get_school_config()
    if config and config.is_configured:
        messages.info(request, 'School is already configured. You can update settings from the admin panel.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Create or update school configuration
                if config:
                    school_config = config
                else:
                    school_config = SchoolConfiguration()
                
                # Basic Information
                school_config.school_name = request.POST.get('school_name')
                school_config.school_type = request.POST.get('school_type')
                school_config.school_motto = request.POST.get('school_motto', '')
                school_config.address = request.POST.get('address')
                school_config.phone = request.POST.get('phone')
                school_config.email = request.POST.get('email')
                school_config.website = request.POST.get('website', '')
                
                # Mark as configured
                school_config.is_configured = True
                school_config.save()
                
                # Create default academic year if it doesn't exist
                current_year = timezone.now().year
                academic_year, created = AcademicYear.objects.get_or_create(
                    year=current_year,
                    defaults={
                        'start_date': timezone.datetime(current_year, 1, 1).date(),
                        'end_date': timezone.datetime(current_year, 12, 31).date(),
                        'is_current': True
                    }
                )
                
                school_config.current_academic_year = academic_year
                school_config.save()
                
                # Create default grades based on school type
                create_default_grades(school_config.school_type)
                
                messages.success(request, f'{school_config.school_name} has been configured successfully!')
                return redirect('accounts:dashboard')
                
        except Exception as e:
            messages.error(request, f'Error during setup: {str(e)}')
    
    context = {
        'config': config,
        'school_types': SchoolConfiguration.SCHOOL_TYPE_CHOICES,
    }
    return render(request, 'accounts/school_setup_wizard.html', context)


def create_default_grades(school_type):
    """Create default grades based on school type"""
    
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


@login_required
@user_passes_test(is_superuser)
def school_settings(request):
    """Update school settings"""
    config = get_school_config()
    
    if not config:
        messages.warning(request, 'Please complete the initial school setup first.')
        return redirect('accounts:school_setup')
    
    if request.method == 'POST':
        try:
            config.school_name = request.POST.get('school_name')
            config.school_motto = request.POST.get('school_motto', '')
            config.address = request.POST.get('address')
            config.phone = request.POST.get('phone')
            config.email = request.POST.get('email')
            config.website = request.POST.get('website', '')
            
            # Update feature flags if provided
            config.enable_library = request.POST.get('enable_library') == 'on'
            config.enable_transport = request.POST.get('enable_transport') == 'on'
            config.enable_hostel = request.POST.get('enable_hostel') == 'on'
            config.enable_parent_portal = request.POST.get('enable_parent_portal') == 'on'
            config.enable_online_classes = request.POST.get('enable_online_classes') == 'on'
            
            config.save()
            
            messages.success(request, 'School settings updated successfully!')
            return redirect('accounts:school_settings')
            
        except Exception as e:
            messages.error(request, f'Error updating settings: {str(e)}')
    
    context = {
        'config': config,
    }
    return render(request, 'accounts/school_settings.html', context)
