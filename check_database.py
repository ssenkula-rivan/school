#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('/home/cranictech/CascadeProjects/school')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workplace_system.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import School
from accounts.models import UserProfile, SchoolConfiguration

print("=" * 60)
print("SCHOOL MANAGEMENT SYSTEM - DATABASE STATUS")
print("=" * 60)

# Check Schools
print("\n🏫 SCHOOLS REGISTERED:")
schools = School.objects.all()
if schools.exists():
    for i, school in enumerate(schools, 1):
        print(f"  {i}. {school.name}")
        print(f"     Type: {school.school_type}")
        print(f"     Code: {school.code}")
        print(f"     Email: {school.email}")
        print(f"     Active: {school.is_active}")
        print(f"     Created: {school.created_at}")
        print()
else:
    print("  ❌ No schools found in database")

print(f"Total Schools: {schools.count()}")

# Check SchoolConfiguration
print("\n⚙️  SCHOOL CONFIGURATIONS:")
configs = SchoolConfiguration.objects.all()
if configs.exists():
    for i, config in enumerate(configs, 1):
        print(f"  {i}. {config.school_name}")
        print(f"     Type: {config.school_type}")
        print(f"     Configured: {config.is_configured}")
        print(f"     Created: {config.created_at}")
        print()
else:
    print("  ❌ No school configurations found")

print(f"Total Configurations: {configs.count()}")

# Check Users
print("\n👥 USERS REGISTERED:")
users = User.objects.all()
if users.exists():
    for i, user in enumerate(users[:10], 1):  # Show first 10
        print(f"  {i}. {user.username}")
        print(f"     Email: {user.email}")
        print(f"     Staff: {user.is_staff}")
        print(f"     Superuser: {user.is_superuser}")
        print(f"     Active: {user.is_active}")
        print(f"     Created: {user.date_joined}")
        print()
    if users.count() > 10:
        print(f"  ... and {users.count() - 10} more users")
else:
    print("  ❌ No users found in database")

print(f"Total Users: {users.count()}")

# Check UserProfiles
print("\n👤 USER PROFILES:")
profiles = UserProfile.objects.all()
if profiles.exists():
    for i, profile in enumerate(profiles[:10], 1):
        print(f"  {i}. {profile.user.username}")
        print(f"     School: {profile.school.name if profile.school else 'None'}")
        print(f"     Role: {profile.role}")
        print(f"     Employee ID: {profile.employee_id}")
        print(f"     Active: {profile.is_active_employee}")
        print()
    if profiles.count() > 10:
        print(f"  ... and {profiles.count() - 10} more profiles")
else:
    print("  ❌ No user profiles found")

print(f"Total Profiles: {profiles.count()}")

print("\n" + "=" * 60)
print("SUMMARY:")
print(f"  Schools: {schools.count()}")
print(f"  Configurations: {configs.count()}")
print(f"  Users: {users.count()}")
print(f"  Profiles: {profiles.count()}")
print("=" * 60)
