#!/usr/bin/env python3
"""
Simple database checker without Django dependencies
"""
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

def get_database_url():
    """Get database URL from environment or render config"""
    # Try environment variable first
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        return database_url
    
    # Try to parse from render.yaml or use defaults
    # For local testing, you might need to set this manually
    return None

def check_database():
    """Check database connection and count schools"""
    database_url = get_database_url()
    
    if not database_url:
        print("❌ No DATABASE_URL found")
        print("Please set DATABASE_URL environment variable")
        print("Example: postgres://user:password@host:port/dbname")
        return
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Database connected successfully")
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print(f"\n📊 Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # Count schools if table exists
        school_tables = [t['table_name'] for t in tables if 'school' in t['table_name'].lower()]
        
        if 'core_school' in school_tables:
            cursor.execute("SELECT COUNT(*) as count FROM core_school;")
            school_count = cursor.fetchone()['count']
            print(f"\n🏫 Schools in database: {school_count}")
            
            if school_count > 0:
                cursor.execute("""
                    SELECT id, name, code, school_type, is_active, created_at 
                    FROM core_school 
                    ORDER BY created_at DESC;
                """)
                schools = cursor.fetchall()
                
                print("\n📋 School Details:")
                for school in schools:
                    status = "✅ Active" if school['is_active'] else "❌ Inactive"
                    print(f"  - {school['name']} ({school['code']}) - {school['school_type']} - {status}")
                    print(f"    Created: {school['created_at']}")
        else:
            print("\n❌ No 'core_school' table found")
        
        # Check users
        if 'auth_user' in [t['table_name'] for t in tables]:
            cursor.execute("SELECT COUNT(*) as count FROM auth_user;")
            user_count = cursor.fetchone()['count']
            print(f"\n👥 Users in database: {user_count}")
            
            if user_count > 0:
                cursor.execute("""
                    SELECT username, email, is_staff, is_superuser, date_joined 
                    FROM auth_user 
                    ORDER BY date_joined DESC 
                    LIMIT 10;
                """)
                users = cursor.fetchall()
                
                print("\n👤 Recent Users:")
                for user in users:
                    staff = "👨‍💼 Staff" if user['is_staff'] else "👤 User"
                    superuser = "🔧 Super" if user['is_superuser'] else ""
                    print(f"  - {user['username']} ({user['email']}) - {staff} {superuser}")
                    print(f"    Joined: {user['date_joined']}")
        
        # Check login attempts
        if 'accounts_loginlog' in [t['table_name'] for t in tables]:
            cursor.execute("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
                       COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                       COUNT(CASE WHEN status = 'blocked' THEN 1 END) as blocked
                FROM accounts_loginlog;
            """)
            login_stats = cursor.fetchone()
            
            print(f"\n🔐 Login Statistics:")
            print(f"  - Total attempts: {login_stats['total']}")
            print(f"  - Successful: {login_stats['successful']}")
            print(f"  - Failed: {login_stats['failed']}")
            print(f"  - Blocked: {login_stats['blocked']}")
            
            if login_stats['total'] > 0:
                cursor.execute("""
                    SELECT username_attempted, status, ip_address, timestamp 
                    FROM accounts_loginlog 
                    ORDER BY timestamp DESC 
                    LIMIT 10;
                """)
                recent_logins = cursor.fetchall()
                
                print("\n📈 Recent Login Attempts:")
                for login in recent_logins:
                    status_icon = "✅" if login['status'] == 'success' else "❌" if login['status'] == 'failed' else "🚫"
                    print(f"  {status_icon} {login['username_attempted']} - {login['ip_address']} - {login['timestamp']}")
        
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Check if DATABASE_URL is correct")
        print("2. Ensure database server is running")
        print("3. Verify network connectivity")
        print("4. Check credentials and permissions")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_database()
