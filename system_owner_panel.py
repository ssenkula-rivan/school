"""
System Owner Panel - For System Developer/Owner Only
Secret URL: /sys-admin-2024/
Access: Superuser Only
Purpose: Manage school payments and access
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import School
from django.contrib.auth.models import User
from accounts.models import UserProfile
import json

def is_superuser(user):
    """Check if user is superuser"""
    return user.is_superuser

def system_owner_dashboard(request):
    """System Owner Dashboard - Manage Schools and Payments (Dev Mode - No Auth Required)"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        school_id = request.POST.get('school_id')
        
        if action == 'update_payment':
            return update_payment_status(request, school_id)
        elif action == 'block_school':
            return block_school_access(request, school_id)
        elif action == 'unblock_school':
            return unblock_school_access(request, school_id)
        elif action == 'delete_school':
            return delete_school_and_data(request, school_id)
    
    # Get all schools with payment and access info
    schools = School.objects.all().order_by('name')
    
    # Handle case when no schools exist
    if not schools.exists():
        context = {
            'schools': [],
            'total_schools': 0,
            'active_schools': 0,
            'blocked_schools': 0,
            'unpaid_schools': 0,
            'total_users': 0,
            'no_schools_message': 'No schools registered yet. Create your first school to get started.',
        }
        return render(request, 'system_owner/dashboard.html', context)
    
    school_data = []
    for school in schools:
        # Get payment info (stored in school metadata or separate model)
        payment_info = get_school_payment_info(school)
        
        # Get user count for this school
        user_count = UserProfile.objects.filter(school=school).count()
        active_users = User.objects.filter(
            userprofile__school=school, 
            is_active=True
        ).count()
        
        # Check if school is blocked
        is_blocked = payment_info.get('is_blocked', False)
        
        school_data.append({
            'id': school.id,
            'name': school.name,
            'code': school.code,
            'email': school.email_domain,  # Fixed: use email_domain instead of email
            'phone': school.phone,
            'contact_person': school.contact_person,
            'is_active': school.is_active,
            'created_at': school.created_at.strftime('%Y-%m-%d') if school.created_at else '',
            'user_count': user_count,
            'active_users': active_users,
            'last_payment': payment_info.get('last_payment', ''),
            'next_payment_due': payment_info.get('next_payment_due', ''),
            'payment_status': payment_info.get('payment_status', 'unpaid'),
            'is_blocked': is_blocked,
            'days_overdue': calculate_days_overdue(payment_info.get('next_payment_due')),
        })
    
    context = {
        'schools': school_data,
        'total_schools': len(school_data),
        'active_schools': len([s for s in school_data if s['is_active'] and not s['is_blocked']]),
        'blocked_schools': len([s for s in school_data if s['is_blocked']]),
        'unpaid_schools': len([s for s in school_data if s['payment_status'] == 'unpaid']),
        'total_users': sum(s['user_count'] for s in school_data),
    }
    
    return render(request, 'system_owner/dashboard.html', context)

def get_school_payment_info(school):
    """Get payment information for a school"""
    # For now, store payment info in school metadata
    # In future, you can create a separate Payment model
    
    # Default payment info
    default_info = {
        'last_payment': None,
        'next_payment_due': None,
        'payment_status': 'unpaid',
        'is_blocked': False,
    }
    
    # Try to get payment info from school metadata (JSON field)
    if hasattr(school, 'metadata'):
        try:
            metadata = school.metadata if isinstance(school.metadata, dict) else {}
            return {
                'last_payment': metadata.get('last_payment', ''),
                'next_payment_due': metadata.get('next_payment_due', ''),
                'payment_status': metadata.get('payment_status', 'unpaid'),
                'is_blocked': metadata.get('is_blocked', False),
            }
        except:
            pass
    
    # Check if school has payment info in a simple way
    # You can customize this based on your actual payment tracking
    payment_date = getattr(school, 'last_payment_date', None)
    next_due = getattr(school, 'next_payment_due_date', None)
    
    return {
        'last_payment': payment_date.strftime('%Y-%m-%d') if payment_date else '',
        'next_payment_due': next_due.strftime('%Y-%m-%d') if next_due else '',
        'payment_status': 'paid' if payment_date and next_due and next_due > timezone.now().date() else 'unpaid',
        'is_blocked': getattr(school, 'is_access_blocked', False),
    }

def calculate_days_overdue(next_payment_due):
    """Calculate days overdue for payment"""
    if not next_payment_due:
        return 0
    
    try:
        due_date = datetime.strptime(next_payment_due, '%Y-%m-%d').date()
        today = timezone.now().date()
        
        if due_date > today:
            return 0
        else:
            return (today - due_date).days
    except:
        return 0

def update_payment_status(request, school_id):
    """Update payment status for a school"""
    try:
        school = School.objects.get(id=school_id)
        last_payment = request.POST.get('last_payment')
        next_payment_due = request.POST.get('next_payment_due')
        payment_status = request.POST.get('payment_status')
        
        # Update school payment info
        # For now, we'll use simple attributes
        if last_payment:
            try:
                school.last_payment_date = datetime.strptime(last_payment, '%Y-%m-%d').date()
            except:
                pass
        
        if next_payment_due:
            try:
                school.next_payment_due_date = datetime.strptime(next_payment_due, '%Y-%m-%d').date()
            except:
                pass
        
        school.save()
        
        messages.success(request, f'Payment information updated for {school.name}')
        
    except Exception as e:
        messages.error(request, f'Error updating payment: {str(e)}')
    
    return redirect('system_owner_dashboard')

def block_school_access(request, school_id):
    """Block access for a school"""
    try:
        school = School.objects.get(id=school_id)
        school.is_access_blocked = True
        school.is_active = False
        school.save()
        
        # Block all users from this school
        UserProfile.objects.filter(school=school).update(is_active_employee=False)
        User.objects.filter(userprofile__school=school).update(is_active=False)
        
        messages.success(request, f'School {school.name} has been blocked. All users access suspended.')
        
    except Exception as e:
        messages.error(request, f'Error blocking school: {str(e)}')
    
    return redirect('system_owner_dashboard')

def unblock_school_access(request, school_id):
    """Unblock access for a school"""
    try:
        school = School.objects.get(id=school_id)
        school.is_access_blocked = False
        school.is_active = True
        school.save()
        
        # Unblock all users from this school
        UserProfile.objects.filter(school=school).update(is_active_employee=True)
        User.objects.filter(userprofile__school=school).update(is_active=True)
        
        messages.success(request, f'School {school.name} has been unblocked. User access restored.')
        
    except Exception as e:
        messages.error(request, f'Error unblocking school: {str(e)}')
    
    return redirect('system_owner_dashboard')

def delete_school_and_data(request, school_id):
    """Delete a school and all its associated data"""
    try:
        school = School.objects.get(id=school_id)
        school_name = school.name
        
        # Get counts before deletion for confirmation message
        user_count = UserProfile.objects.filter(school=school).count()
        
        # Delete all users associated with this school
        # This will cascade delete UserProfiles due to ForeignKey relationships
        users_to_delete = User.objects.filter(userprofile__school=school)
        users_to_delete.delete()
        
        # Delete the school (this will cascade delete all related data)
        # Due to Django's CASCADE behavior, this will delete:
        # - All students, teachers, staff
        # - All classes, subjects, exams, marks
        # - All attendance records
        # - All academic years
        # - All other related data
        school.delete()
        
        messages.success(
            request, 
            f'✅ School "{school_name}" and all associated data deleted successfully. '
            f'({user_count} users and all related records removed)'
        )
        
    except School.DoesNotExist:
        messages.error(request, 'School not found.')
    except Exception as e:
        messages.error(request, f'Error deleting school: {str(e)}')
    
    return redirect('system_owner_dashboard')

def school_payment_api(request, school_id):
    """API endpoint for payment updates (Dev Mode - No Auth Required)"""
    if request.method == 'POST':
        try:
            school = School.objects.get(id=school_id)
            data = json.loads(request.body)
            
            # Update payment info
            if 'last_payment' in data:
                try:
                    school.last_payment_date = datetime.strptime(data['last_payment'], '%Y-%m-%d').date()
                except:
                    pass
            
            if 'next_payment_due' in data:
                try:
                    school.next_payment_due_date = datetime.strptime(data['next_payment_due'], '%Y-%m-%d').date()
                except:
                    pass
            
            if 'payment_status' in data:
                # Auto-calculate status based on dates if not provided
                if data['payment_status'] == 'auto':
                    if school.next_payment_due_date and school.next_payment_due_date > timezone.now().date():
                        status = 'paid'
                    else:
                        status = 'unpaid'
                else:
                    status = data['payment_status']
            else:
                status = 'paid' if school.next_payment_due_date and school.next_payment_due_date > timezone.now().date() else 'unpaid'
            
            school.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Payment updated for {school.name}',
                'payment_status': status
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
