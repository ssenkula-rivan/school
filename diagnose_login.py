"""
Diagnose login issues - Check database state
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workplace_system.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from core.models import School

def check_database_state():
    """Check what's actually in the database"""
    print("=== DATABASE DIAGNOSTIC ===")
    
    # Check users
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    
    # Check superusers
    superusers = User.objects.filter(is_superuser=True)
    print(f"Superusers: {superusers.count()}")
    for su in superusers:
        print(f"  - {su.username} (active: {su.is_active})")
    
    # Check schools
    schools = School.objects.all()
    print(f"Total schools: {schools.count()}")
    for school in schools:
        print(f"  - {school.name} (active: {school.is_active})")
    
    # Check user profiles
    profiles = UserProfile.objects.all()
    print(f"User profiles: {profiles.count()}")
    
    # Check for orphaned users (users without profiles)
    orphaned_users = User.objects.filter(userprofile__isnull=True)
    print(f"Orphaned users (no profile): {orphaned_users.count()}")
    
    # Check for profiles without schools
    profiles_without_school = UserProfile.objects.filter(school__isnull=True)
    print(f"Profiles without school: {profiles_without_school.count()}")
    
    print("=== END DIAGNOSTIC ===")

if __name__ == '__main__':
    check_database_state()
