"""
Database diagnostic view - for checking production database without shell access
"""
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.conf import settings
from .models import UserProfile
import os


def database_diagnostic(request):
    """
    Show database state - protected by SECRET_KEY
    For Render free tier users without shell access
    """
    # Check if SECRET_KEY is provided
    provided_key = request.GET.get('key', '')
    
    if not provided_key:
        return HttpResponse("""
        <html>
        <head><title>Database Diagnostic</title></head>
        <body style="font-family: monospace; padding: 20px;">
            <h2>Database Diagnostic Tool</h2>
            <p>This tool shows the current database state.</p>
            <p>Add <code>?key=YOUR_SECRET_KEY</code> to the URL to access.</p>
            <p>Example: <code>/accounts/db-check/?key=your-secret-key-here</code></p>
        </body>
        </html>
        """, content_type='text/html')
    
    # Verify SECRET_KEY
    if provided_key != settings.SECRET_KEY:
        return HttpResponse("""
        <html>
        <head><title>Access Denied</title></head>
        <body style="font-family: monospace; padding: 20px; color: red;">
            <h2>Access Denied</h2>
            <p>Invalid SECRET_KEY provided.</p>
            <p>Get your SECRET_KEY from Render environment variables.</p>
        </body>
        </html>
        """, content_type='text/html', status=403)
    
    # Collect database information
    output = []
    output.append("=" * 80)
    output.append("DATABASE DIAGNOSTIC REPORT")
    output.append("=" * 80)
    output.append("")
    
    # Environment info
    output.append("ENVIRONMENT:")
    output.append(f"  DEBUG: {settings.DEBUG}")
    output.append(f"  DATABASE: {settings.DATABASES['default']['ENGINE']}")
    output.append(f"  DATABASE_URL set: {'DATABASE_URL' in os.environ}")
    output.append("")
    
    # User count
    user_count = User.objects.count()
    output.append(f"TOTAL USERS: {user_count}")
    output.append("")
    
    if user_count == 0:
        output.append("  NO USERS FOUND IN DATABASE")
        output.append("   You need to register a school first!")
        output.append("")
    else:
        output.append("USER DETAILS:")
        output.append("-" * 80)
        
        for u in User.objects.all().order_by('-date_joined'):
            output.append("")
            output.append(f"USERNAME: {u.username}")
            output.append(f"  Email: {u.email}")
            output.append(f"  Active: {u.is_active}")
            output.append(f"  Staff: {u.is_staff}")
            output.append(f"  Superuser: {u.is_superuser}")
            output.append(f"  Date Joined: {u.date_joined}")
            output.append(f"  Last Login: {u.last_login}")
            
            # Check password hash
            pw_hashed = u.password.startswith(('pbkdf2_sha256$', 'argon2$', 'bcrypt$'))
            if pw_hashed:
                output.append(f"  Password: ✅ HASHED (secure)")
                output.append(f"  Password Preview: {u.password[:50]}...")
            else:
                output.append(f"  Password: ❌ PLAIN TEXT (INSECURE!)")
                output.append(f"  Password Value: {u.password}")
            
            # Check profile
            try:
                profile = u.userprofile
                output.append(f"  Profile: ✅ EXISTS")
                output.append(f"    Employee ID: {profile.employee_id}")
                output.append(f"    Role: {profile.role}")
                output.append(f"    School: {profile.school.name if profile.school else 'NO SCHOOL'}")
                output.append(f"    Active Employee: {profile.is_active_employee}")
                output.append(f"    Currently Logged In: {profile.is_currently_logged_in}")
            except UserProfile.DoesNotExist:
                output.append(f"  Profile: ❌ MISSING")
            except Exception as e:
                output.append(f"  Profile: ⚠️  ERROR - {str(e)}")
    
    output.append("")
    output.append("-" * 80)
    
    # School count
    from core.models import School
    school_count = School.objects.count()
    output.append(f"TOTAL SCHOOLS: {school_count}")
    
    if school_count > 0:
        output.append("")
        output.append("SCHOOL DETAILS:")
        for school in School.objects.all()[:10]:  # Limit to 10
            output.append(f"  - {school.name} ({school.code})")
            output.append(f"    Type: {school.school_type}")
            output.append(f"    Active: {school.is_active}")
            output.append(f"    Email: {school.email}")
    
    output.append("")
    output.append("=" * 80)
    output.append("END OF REPORT")
    output.append("=" * 80)
    
    # Return as HTML with monospace font
    html_output = "<html><head><title>Database Diagnostic</title></head>"
    html_output += "<body style='font-family: monospace; padding: 20px; background: #1e1e1e; color: #d4d4d4;'>"
    html_output += "<pre style='white-space: pre-wrap; word-wrap: break-word;'>"
    html_output += "\n".join(output)
    html_output += "</pre>"
    html_output += "<hr>"
    html_output += "<p><a href='/accounts/login/' style='color: #4fc3f7;'>Go to Login Page</a> | "
    html_output += "<a href='/accounts/register-school/' style='color: #4fc3f7;'>Register School</a></p>"
    html_output += "</body></html>"
    
    return HttpResponse(html_output, content_type='text/html')
