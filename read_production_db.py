#!/usr/bin/env python3
"""
Read-only database query - no Django dependencies
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def read_production_database():
    """Read exact school count from production database - READ ONLY"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        print("This script needs to run on production server")
        return 0
    
    try:
        print("🔍 CONNECTING TO PRODUCTION DATABASE - READ ONLY")
        print("=" * 55)
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Database connected successfully")
        
        # Check if core_school table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'core_school'
            );
        """)
        school_table_exists = cursor.fetchone()['exists']
        
        if school_table_exists:
            # Get exact school count
            cursor.execute("SELECT COUNT(*) as count FROM core_school;")
            school_count = cursor.fetchone()['count']
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
                for i, school in enumerate(schools, 1):
                    status = "Active" if school['is_active'] else "Inactive"
                    print(f"  {i}. {school['name']} ({school['code']})")
                    print(f"     Type: {school['school_type']}")
                    print(f"     Status: {status}")
                    print(f"     Created: {school['created_at']}")
                    print()
            else:
                print("  No schools found in database")
        else:
            print("❌ core_school table does not exist")
            school_count = 0
        
        # Get user count
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'auth_user'
            );
        """)
        user_table_exists = cursor.fetchone()['exists']
        
        if user_table_exists:
            cursor.execute("SELECT COUNT(*) as count FROM auth_user;")
            user_count = cursor.fetchone()['count']
            print(f"👥 Users: {user_count}")
        
        # Get student count
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'core_student'
            );
        """)
        student_table_exists = cursor.fetchone()['exists']
        
        if student_table_exists:
            cursor.execute("SELECT COUNT(*) as count FROM core_student;")
            student_count = cursor.fetchone()['count']
            print(f"🎓 Students: {student_count}")
        
        conn.close()
        
        print("\n" + "=" * 55)
        print("✅ READ OPERATION COMPLETED - NO MODIFICATIONS MADE")
        
        return school_count
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

if __name__ == "__main__":
    exact_count = read_production_database()
    print(f"\n📊 EXACT ANSWER: {exact_count} schools registered in production")
