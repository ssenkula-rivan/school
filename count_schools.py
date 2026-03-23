#!/usr/bin/env python
import os
import sys

# Add the project directory to Python path
sys.path.insert(0, '/home/cranictech/CascadeProjects/school')

# Set Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'workplace_system.settings'

# Try to query database directly without Django setup first
try:
    import sqlite3
    print("Checking for local SQLite database...")
    
    # Look for SQLite database files
    import glob
    db_files = glob.glob('/home/cranictech/CascadeProjects/school/*.db') + \
                glob.glob('/home/cranictech/CascadeProjects/school/*.sqlite3') + \
                glob.glob('/home/cranictech/CascadeProjects/school/db/*.db') + \
                glob.glob('/home/cranictech/CascadeProjects/school/db/*.sqlite3')
    
    if db_files:
        print(f"Found database files: {db_files}")
        for db_file in db_files:
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Check tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"\nTables in {db_file}: {[table[0] for table in tables]}")
                
                # Check schools
                if any('school' in table[0].lower() for table in tables):
                    try:
                        cursor.execute("SELECT COUNT(*) FROM core_school")
                        school_count = cursor.fetchone()[0]
                        print(f"Schools in core_school: {school_count}")
                        
                        if school_count > 0:
                            cursor.execute("SELECT name, school_type, code FROM core_school LIMIT 10")
                            schools = cursor.fetchall()
                            print("Registered schools:")
                            for i, school in enumerate(schools, 1):
                                print(f"  {i}. {school[0]} ({school[1]}) - {school[2]}")
                    except:
                        print("Could not query core_school table")
                
                # Check users
                if any('auth_user' in table[0].lower() for table in tables):
                    try:
                        cursor.execute("SELECT COUNT(*) FROM auth_user")
                        user_count = cursor.fetchone()[0]
                        print(f"Users in auth_user: {user_count}")
                        
                        if user_count > 0:
                            cursor.execute("SELECT username, email, is_staff FROM auth_user LIMIT 10")
                            users = cursor.fetchall()
                            print("Registered users:")
                            for i, user in enumerate(users, 1):
                                print(f"  {i}. {user[0]} ({user[1]}) - Staff: {user[2]}")
                    except:
                        print("Could not query auth_user table")
                
                conn.close()
            except Exception as e:
                print(f"Error reading {db_file}: {e}")
    else:
        print("No local SQLite database files found")
        print("This suggests using PostgreSQL on Render")

except ImportError:
    print("SQLite not available")

# Try Django approach
try:
    import django
    from django.conf import settings
    
    # Configure Django
    if not settings.configured:
        django.setup()
    
    print("\n" + "="*60)
    print("DJANGO DATABASE QUERY")
    print("="*60)
    
    # Check database configuration
    print(f"Database engine: {settings.DATABASES['default']['ENGINE']}")
    print(f"Database name: {settings.DATABASES['default']['NAME']}")
    
    # Try to query models
    try:
        from django.contrib.auth.models import User
        user_count = User.objects.count()
        print(f"Total Users: {user_count}")
        
        if user_count > 0:
            users = User.objects.all()[:10]
            print("Users:")
            for i, user in enumerate(users, 1):
                print(f"  {i}. {user.username} ({user.email})")
                
    except Exception as e:
        print(f"Error querying users: {e}")
    
    try:
        from core.models import School
        school_count = School.objects.count()
        print(f"Total Schools: {school_count}")
        
        if school_count > 0:
            schools = School.objects.all()[:10]
            print("Schools:")
            for i, school in enumerate(schools, 1):
                print(f"  {i}. {school.name} ({school.school_type})")
                
    except Exception as e:
        print(f"Error querying schools: {e}")
        
    try:
        from accounts.models import SchoolConfiguration
        config_count = SchoolConfiguration.objects.count()
        print(f"Total School Configurations: {config_count}")
        
        if config_count > 0:
            configs = SchoolConfiguration.objects.all()[:10]
            print("School Configurations:")
            for i, config in enumerate(configs, 1):
                print(f"  {i}. {config.school_name} ({config.school_type})")
                
    except Exception as e:
        print(f"Error querying school configurations: {e}")
        
except ImportError as e:
    print(f"Django import error: {e}")
    
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("If you see '0' for all counts, the database is empty.")
print("If you see errors, database connection is failing.")
print("="*60)
