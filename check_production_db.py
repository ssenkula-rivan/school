#!/usr/bin/env python3
"""
Check production database schools count
"""
import os
import sys
import django

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workplace_system.settings')
    django.setup()

def check_schools():
    """Check exact number of schools in production"""
    from core.models import School
    from django.contrib.auth.models import User
    from accounts.models import UserProfile
    
    try:
        print("🔍 PRODUCTION DATABASE CHECK")
        print("=" * 40)
        
        # Count schools
        school_count = School.objects.count()
        print(f"🏫 Schools: {school_count}")
        
        if school_count > 0:
            schools = School.objects.all().order_by('-created_at')
            print("\n📋 School Details:")
            for school in schools:
                status = "✅ Active" if school.is_active else "❌ Inactive"
                print(f"  - {school.name} ({school.code})")
                print(f"    Type: {school.school_type} - {school.institution_type}")
                print(f"    Status: {status}")
                print(f"    Email: {school.email}")
                print(f"    Created: {school.created_at}")
                print(f"    Subscription: {school.subscription_start} to {school.subscription_end}")
                print(f"    Max Students: {school.max_students}, Max Staff: {school.max_staff}")
                print()
        
        # Count users
        user_count = User.objects.count()
        profile_count = UserProfile.objects.count()
        print(f"👥 Users: {user_count} total, {profile_count} with profiles")
        
        # Count students
        from core.models import Student
        student_count = Student.objects.count()
        print(f"🎓 Students: {student_count}")
        
        # Check admin user
        try:
            admin_user = User.objects.get(username='admin')
            admin_profile = UserProfile.objects.filter(user=admin_user).first()
            print(f"\n🔑 Admin User:")
            print(f"  Username: {admin_user.username}")
            print(f"  Email: {admin_user.email}")
            print(f"  Staff: {admin_user.is_staff}")
            print(f"  Superuser: {admin_user.is_superuser}")
            print(f"  Active: {admin_user.is_active}")
            if admin_profile:
                print(f"  Profile: ✅ Exists (Role: {admin_profile.role})")
            else:
                print(f"  Profile: ❌ Missing")
        except User.DoesNotExist:
            print(f"\n❌ No admin user found")
        
        return school_count
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return 0

if __name__ == "__main__":
    setup_django()
    school_count = check_schools()
    print(f"\n📊 FINAL COUNT: {school_count} school(s) registered")
