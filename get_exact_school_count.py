#!/usr/bin/env python3
"""
Read-only script to get exact school count from production database
No modifications, only reads data
"""
import os
import sys
import django

def setup_django():
    """Setup Django environment for reading"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workplace_system.settings')
    django.setup()

def get_exact_counts():
    """Read exact counts from production database - READ ONLY"""
    try:
        from django.db import connection
        
        print("🔍 EXACT DATABASE COUNTS - READ ONLY")
        print("=" * 50)
        
        # Use raw SQL to get exact counts
        with connection.cursor() as cursor:
            
            # Check if core_school table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'core_school'
                );
            """)
            school_table_exists = cursor.fetchone()[0]
            
            if school_table_exists:
                # Get exact school count
                cursor.execute("SELECT COUNT(*) FROM core_school;")
                school_count = cursor.fetchone()[0]
                print(f"🏫 Schools: {school_count}")
                
                # Get school details if any exist
                if school_count > 0:
                    cursor.execute("""
                        SELECT id, name, code, school_type, is_active, created_at 
                        FROM core_school 
                        ORDER BY created_at;
                    """)
                    schools = cursor.fetchall()
                    
                    print("\n📋 School Details:")
                    for school in schools:
                        status = "Active" if school[4] else "Inactive"
                        print(f"  ID: {school[0]}")
                        print(f"  Name: {school[1]}")
                        print(f"  Code: {school[2]}")
                        print(f"  Type: {school[3]}")
                        print(f"  Status: {status}")
                        print(f"  Created: {school[5]}")
                        print()
                else:
                    print("  No schools found in database")
            else:
                print("❌ core_school table does not exist")
            
            # Get user count
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'auth_user'
                );
            """)
            user_table_exists = cursor.fetchone()[0]
            
            if user_table_exists:
                cursor.execute("SELECT COUNT(*) FROM auth_user;")
                user_count = cursor.fetchone()[0]
                print(f"👥 Users: {user_count}")
            
            # Get student count
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'core_student'
                );
            """)
            student_table_exists = cursor.fetchone()[0]
            
            if student_table_exists:
                cursor.execute("SELECT COUNT(*) FROM core_student;")
                student_count = cursor.fetchone()[0]
                print(f"🎓 Students: {student_count}")
        
        print("\n" + "=" * 50)
        print("✅ READ OPERATION COMPLETED - NO MODIFICATIONS MADE")
        
        return school_count if school_table_exists else 0
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        return 0

if __name__ == "__main__":
    setup_django()
    exact_count = get_exact_counts()
    print(f"\n📊 FINAL ANSWER: {exact_count} schools registered")
