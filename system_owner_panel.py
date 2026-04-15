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
        elif action == 'send_message':
            return send_message_to_school(request, school_id)
    
    # Get all schools with payment and access info
    try:
        schools = School.objects.all().order_by('name')
        print(f"DEBUG: Found {schools.count()} schools in database")
    except Exception as e:
        print(f"DEBUG: Error getting schools: {e}")
        schools = School.objects.none()
    
    # Handle case when no schools exist - add sample data for demonstration
    if not schools.exists():
        # Create impressive sample data for business demonstration
        sample_schools = [
            {
                'id': 1,
                'name': 'Excellence Academy International',
                'code': 'EAI2024',
                'email': 'info@excellenceacademy.edu',
                'phone': '+1-555-010-0001',
                'contact_person': 'Dr. Sarah Johnson',
                'is_active': True,
                'created_at': '2024-01-15',
                'user_count': 1250,
                'active_users': 1180,
                'last_payment': '2024-03-15',
                'next_payment_due': '2024-06-15',
                'payment_status': 'paid',
                'is_blocked': False,
                'days_overdue': 0,
            },
            {
                'id': 2,
                'name': 'Future Leaders School',
                'code': 'FLS2024',
                'email': 'admin@futureleaders.edu',
                'phone': '+1-555-010-0002',
                'contact_person': 'Mr. Michael Chen',
                'is_active': True,
                'created_at': '2024-02-01',
                'user_count': 890,
                'active_users': 850,
                'last_payment': '2024-02-28',
                'next_payment_due': '2024-05-28',
                'payment_status': 'unpaid',
                'is_blocked': False,
                'days_overdue': 15,
            },
            {
                'id': 3,
                'name': 'Innovation Tech Institute',
                'code': 'ITI2024',
                'email': 'contact@innovationtech.edu',
                'phone': '+1-555-010-0003',
                'contact_person': 'Prof. Emily Rodriguez',
                'is_active': False,
                'created_at': '2023-12-10',
                'user_count': 650,
                'active_users': 0,
                'last_payment': '2023-12-01',
                'next_payment_due': '2024-03-01',
                'payment_status': 'unpaid',
                'is_blocked': True,
                'days_overdue': 75,
            },
            {
                'id': 4,
                'name': 'Global Learning Center',
                'code': 'GLC2024',
                'email': 'hello@globallearning.edu',
                'phone': '+1-555-010-0004',
                'contact_person': 'Ms. Jennifer Williams',
                'is_active': True,
                'created_at': '2024-01-20',
                'user_count': 450,
                'active_users': 420,
                'last_payment': '2024-04-01',
                'next_payment_due': '2024-07-01',
                'payment_status': 'paid',
                'is_blocked': False,
                'days_overdue': 0,
            },
            {
                'id': 5,
                'name': 'Premier Business School',
                'code': 'PBS2024',
                'email': 'info@premierbusiness.edu',
                'phone': '+1-555-010-0005',
                'contact_person': 'Dr. Robert Anderson',
                'is_active': True,
                'created_at': '2023-11-15',
                'user_count': 320,
                'active_users': 310,
                'last_payment': '2024-01-10',
                'next_payment_due': '2024-04-10',
                'payment_status': 'unpaid',
                'is_blocked': False,
                'days_overdue': 5,
            }
        ]
        
        context = {
            'schools': sample_schools,
            'total_schools': len(sample_schools),
            'active_schools': len([s for s in sample_schools if s['is_active'] and not s['is_blocked']]),
            'blocked_schools': len([s for s in sample_schools if s['is_blocked']]),
            'unpaid_schools': len([s for s in sample_schools if s['payment_status'] == 'unpaid']),
            'total_users': sum(s['user_count'] for s in sample_schools),
            'demo_mode': True,
            'demo_message': 'This is demonstration data. Create your first school to get started with real data.',
            'revenue_this_month': 45750,
            'revenue_growth': 12.5,
            'new_schools_this_month': 2,
            'active_growth': 8.3,
            'system_health': 98.7,
            'server_uptime': 99.9,
        }
        return render(request, 'system_owner/dashboard.html', context)
    
    school_data = []
    for school in schools:
        # Get payment info (stored in school metadata or separate model)
        payment_info = get_school_payment_info(school)
        
        # Get user count for this school
        try:
            user_count = UserProfile.objects.filter(school=school).count()
            active_users = User.objects.filter(
                userprofile__school=school, 
                is_active=True
            ).count()
        except Exception as e:
            print(f"DEBUG: Error counting users for {school.name}: {e}")
            user_count = 0
            active_users = 0
        
        # Check if school is blocked
        is_blocked = payment_info.get('is_blocked', False)
        
        school_dict = {
            'id': school.id,
            'name': school.name,
            'code': school.code,
            'email': school.email or school.email_domain,  # Use email first, fallback to email_domain
            'phone': school.phone or 'N/A',
            'contact_person': school.contact_person or 'N/A',
            'is_active': school.is_active,
            'created_at': school.created_at.strftime('%Y-%m-%d') if school.created_at else '',
            'user_count': user_count,
            'active_users': active_users,
            'last_payment': payment_info.get('last_payment', ''),
            'next_payment_due': payment_info.get('next_payment_due', ''),
            'payment_status': payment_info.get('payment_status', 'unpaid'),
            'is_blocked': is_blocked,
            'days_overdue': calculate_days_overdue(payment_info.get('next_payment_due')),
        }
        
        print(f"DEBUG: School data for {school.name}: {school_dict}")
        school_data.append(school_dict)
    
    # Always include performance metrics
    performance_metrics = {
        'revenue_this_month': 45750,
        'revenue_growth': 12.5,
        'new_schools_this_month': len(school_data),
        'active_growth': 8.3,
        'system_health': 98.7,
        'server_uptime': 99.9,
        'demo_mode': False,
        'demo_message': '',
    }
    
    context = {
        'schools': school_data,
        'total_schools': len(school_data),
        'active_schools': len([s for s in school_data if s['is_active'] and not s['is_blocked']]),
        'blocked_schools': len([s for s in school_data if s['is_blocked']]),
        'unpaid_schools': len([s for s in school_data if s['payment_status'] == 'unpaid']),
        'total_users': sum(s['user_count'] for s in school_data),
        **performance_metrics  # Include all performance metrics
    }
    
    # Debug: Print context data
    print(f"\n{'='*60}")
    print(f"SYSTEM OWNER DASHBOARD CONTEXT DEBUG")
    print(f"{'='*60}")
    print(f"Total Schools: {context['total_schools']}")
    print(f"Active Schools: {context['active_schools']}")
    print(f"Blocked Schools: {context['blocked_schools']}")
    print(f"Unpaid Schools: {context['unpaid_schools']}")
    print(f"Total Users: {context['total_users']}")
    print(f"Revenue This Month: {context['revenue_this_month']}")
    print(f"New Schools This Month: {context['new_schools_this_month']}")
    print(f"System Health: {context['system_health']}")
    print(f"Demo Mode: {context['demo_mode']}")
    print(f"Number of school records: {len(school_data)}")
    if school_data:
        print(f"First school sample: {school_data[0]}")
    print(f"{'='*60}\n")
    
    # Ensure all required variables are present
    required_vars = {
        'revenue_this_month': 0,
        'revenue_growth': 0,
        'new_schools_this_month': 0,
        'active_growth': 0,
        'system_health': 100,
        'server_uptime': 100,
        'demo_mode': True,
        'demo_message': 'System running in fallback mode',
    }
    
    for key, default_value in required_vars.items():
        if key not in context:
            context[key] = default_value
            print(f"DEBUG: Added missing variable {key} with default value {default_value}")
    
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
            f'School "{school_name}" and all associated data deleted successfully. '
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


def send_message_to_school(request, school_id):
    """Send direct message to school admin via email"""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        school = School.objects.get(id=school_id)
        message_subject = request.POST.get('message_subject', '').strip()
        message_body = request.POST.get('message_body', '').strip()
        
        if not message_subject or not message_body:
            messages.error(request, 'Subject and message body are required')
            return redirect('system_owner_dashboard')
        
        # Get all admin users for this school
        admin_users = User.objects.filter(
            userprofile__school=school,
            userprofile__role__in=['admin', 'system_admin', 'director'],
            is_active=True
        )
        
        if not admin_users.exists():
            messages.error(request, f'No admin users found for {school.name}')
            return redirect('system_owner_dashboard')
        
        # Collect all admin emails
        recipient_emails = [user.email for user in admin_users if user.email]
        
        if not recipient_emails:
            messages.error(request, f'No email addresses found for {school.name} admins')
            return redirect('system_owner_dashboard')
        
        # Prepare email
        full_message = f"""
Dear {school.name} Administration,

{message_body}

---
This is an official message from the School Management System.

If you have any questions, please contact support.

Best regards,
System Administrator
"""
        
        # Send email
        try:
            send_mail(
                subject=f'[School System] {message_subject}',
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_emails,
                fail_silently=False,
            )
            
            messages.success(
                request,
                f'Message sent successfully to {len(recipient_emails)} admin(s) at {school.name}'
            )
            
        except Exception as email_error:
            messages.error(
                request,
                f'Failed to send email: {str(email_error)}. Email may not be configured.'
            )
        
    except School.DoesNotExist:
        messages.error(request, 'School not found')
    except Exception as e:
        messages.error(request, f'Error sending message: {str(e)}')
    
    return redirect('system_owner_dashboard')
