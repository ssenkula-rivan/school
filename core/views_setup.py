"""
Setup views for initializing school data (departments, positions)
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.management import call_command
from io import StringIO
from accounts.decorators import role_required


@login_required
@role_required('admin', 'system_admin')
def setup_school_data(request):
    """Initialize school with default departments and positions"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        try:
            user_profile = request.user.userprofile
            school_code = user_profile.school.code
            
            output = StringIO()
            
            if action == 'departments':
                call_command('create_default_departments', school_code=school_code, stdout=output)
                messages.success(request, f' Departments created successfully!\n{output.getvalue()}')
            
            elif action == 'positions':
                call_command('create_default_positions', school_code=school_code, stdout=output)
                messages.success(request, f' Positions created successfully!\n{output.getvalue()}')
            
            elif action == 'both':
                call_command('create_default_departments', school_code=school_code, stdout=output)
                call_command('create_default_positions', school_code=school_code, stdout=output)
                messages.success(request, f' Departments and Positions created successfully!\n{output.getvalue()}')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    # Get current counts
    try:
        from core.models import Department
        from employees.models import Position
        user_profile = request.user.userprofile
        
        dept_count = Department.objects.filter(school=user_profile.school).count()
        pos_count = Position.objects.filter(school=user_profile.school).count()
        
        context = {
            'dept_count': dept_count,
            'pos_count': pos_count,
        }
    except:
        context = {}
    
    return render(request, 'core/setup_school_data.html', context)
