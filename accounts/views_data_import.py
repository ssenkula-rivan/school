"""
Data Import Views
Interface for importing existing school data
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .data_import import (
    StudentImporter, EmployeeImporter, DatabaseConnector,
    generate_import_template
)
from .school_config import get_school_config
import csv
import os


def is_admin(user):
    return user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin')


@login_required
@user_passes_test(is_admin)
def data_import_dashboard(request):
    """Main data import dashboard"""
    config = get_school_config()
    
    context = {
        'config': config,
    }
    return render(request, 'accounts/data_import_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def import_students(request):
    """Import students from file"""
    if request.method == 'POST':
        if 'file' not in request.FILES:
            messages.error(request, 'No file uploaded')
            return redirect('accounts:data_import')
        
        file = request.FILES['file']
        file_ext = os.path.splitext(file.name)[1].lower()
        
        # Save file temporarily
        temp_path = f'/tmp/{file.name}'
        with open(temp_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Import based on file type
        config = get_school_config()
        importer = StudentImporter(config)
        
        try:
            if file_ext == '.csv':
                importer.import_from_csv(temp_path)
            elif file_ext in ['.xlsx', '.xls']:
                importer.import_from_excel(temp_path)
            else:
                messages.error(request, 'Unsupported file format. Use CSV or Excel.')
                return redirect('accounts:data_import')
            
            # Get report
            report = importer.get_report()
            
            messages.success(
                request,
                f"Import completed! Success: {report['success']}, "
                f"Skipped: {report['skipped']}, Errors: {report['errors']}"
            )
            
            if report['errors'] > 0:
                # Store errors in session for display
                request.session['import_errors'] = report['error_details']
            
        except Exception as e:
            messages.error(request, f'Import failed: {str(e)}')
        
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        return redirect('accounts:data_import')
    
    return render(request, 'accounts/import_students.html')


@login_required
@user_passes_test(is_admin)
def import_employees(request):
    """Import employees from file"""
    if request.method == 'POST':
        if 'file' not in request.FILES:
            messages.error(request, 'No file uploaded')
            return redirect('accounts:data_import')
        
        file = request.FILES['file']
        file_ext = os.path.splitext(file.name)[1].lower()
        
        # Save file temporarily
        temp_path = f'/tmp/{file.name}'
        with open(temp_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Import
        config = get_school_config()
        importer = EmployeeImporter(config)
        
        try:
            if file_ext == '.csv':
                importer.import_from_csv(temp_path)
            else:
                messages.error(request, 'Only CSV format supported for employees')
                return redirect('accounts:data_import')
            
            report = importer.get_report()
            messages.success(
                request,
                f"Import completed! Success: {report['success']}, "
                f"Skipped: {report['skipped']}, Errors: {report['errors']}"
            )
            
        except Exception as e:
            messages.error(request, f'Import failed: {str(e)}')
        
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        return redirect('accounts:data_import')
    
    return render(request, 'accounts/import_employees.html')


@login_required
@user_passes_test(is_admin)
def download_template(request, data_type):
    """Download CSV template for data import"""
    headers = generate_import_template(data_type)
    
    if not headers:
        messages.error(request, 'Invalid data type')
        return redirect('accounts:data_import')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{data_type}_import_template.csv"'
    
    writer = csv.writer(response)
    writer.writerow(headers)
    
    # Add sample row
    sample_data = {
        'students': ['STD001', 'John', 'Doe', 'M', '2010-01-15', 'M', 'Primary 1', '2024-01-01', 'active', 
                    'john@example.com', '+256700000000', '123 Main St', 'Jane Doe', 'Mother', '+256700000001', 
                    'jane@example.com', 'O+'],
        'employees': ['EMP001', 'Jane', 'Smith', 'jane@school.com', '+256700000002', 'Administration', 
                     'Teacher', '1985-05-20', '2020-01-01', 'active', '500000', 'janesmith'],
        'fees': ['STD001', '500000', '2024-01-15', 'cash', 'REF001', '2024']
    }
    
    if data_type in sample_data:
        writer.writerow(sample_data[data_type])
    
    return response


@login_required
@user_passes_test(is_admin)
def test_database_connection(request):
    """Test external database connection"""
    if request.method == 'POST':
        db_type = request.POST.get('db_type')
        host = request.POST.get('host')
        port = request.POST.get('port')
        database = request.POST.get('database')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        success, message = DatabaseConnector.test_connection(
            db_type, host, port, database, username, password
        )
        
        return JsonResponse({
            'success': success,
            'message': message
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
@user_passes_test(is_admin)
def import_from_database(request):
    """Import data from external database"""
    if request.method == 'POST':
        db_type = request.POST.get('db_type')
        host = request.POST.get('host')
        port = request.POST.get('port')
        database = request.POST.get('database')
        username = request.POST.get('username')
        password = request.POST.get('password')
        table_name = request.POST.get('table_name')
        data_type = request.POST.get('data_type')
        
        result = DatabaseConnector.import_from_database(
            db_type, host, port, database, username, password,
            table_name, data_type
        )
        
        if result['success']:
            messages.success(request, result['message'])
        else:
            messages.error(request, result['message'])
        
        return redirect('accounts:data_import')
    
    return render(request, 'accounts/import_from_database.html')
