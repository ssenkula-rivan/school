"""
Department management views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department
from accounts.decorators import role_required


@login_required
@role_required('admin', 'director', 'hr_manager')
def department_list(request):
    """List all departments for the school"""
    try:
        user_profile = request.user.userprofile
        departments = Department.objects.filter(
            school=user_profile.school
        ).order_by('name')
        
        context = {
            'departments': departments,
        }
        return render(request, 'core/department_list.html', context)
    except:
        messages.error(request, 'Error loading departments')
        return redirect('accounts:dashboard')


@login_required
@role_required('admin', 'director', 'hr_manager')
def department_create(request):
    """Create a new department"""
    if request.method == 'POST':
        try:
            user_profile = request.user.userprofile
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            
            if not name:
                messages.error(request, 'Department name is required')
                return redirect('core:department_create')
            
            # Check if department already exists
            if Department.objects.filter(school=user_profile.school, name=name).exists():
                messages.error(request, f'Department "{name}" already exists')
                return redirect('core:department_create')
            
            department = Department.objects.create(
                school=user_profile.school,
                name=name,
                description=description,
                is_active=True
            )
            
            messages.success(request, f'Department "{name}" created successfully')
            return redirect('core:department_list')
            
        except Exception as e:
            messages.error(request, f'Error creating department: {str(e)}')
            return redirect('core:department_create')
    
    return render(request, 'core/department_form.html', {'action': 'Create'})


@login_required
@role_required('admin', 'director', 'hr_manager')
def department_edit(request, pk):
    """Edit a department"""
    try:
        user_profile = request.user.userprofile
        department = get_object_or_404(
            Department,
            pk=pk,
            school=user_profile.school
        )
        
        if request.method == 'POST':
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            is_active = request.POST.get('is_active') == 'on'
            
            if not name:
                messages.error(request, 'Department name is required')
                return redirect('core:department_edit', pk=pk)
            
            department.name = name
            department.description = description
            department.is_active = is_active
            department.save()
            
            messages.success(request, f'Department "{name}" updated successfully')
            return redirect('core:department_list')
        
        context = {
            'department': department,
            'action': 'Edit'
        }
        return render(request, 'core/department_form.html', context)
        
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('core:department_list')
