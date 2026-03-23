#!/usr/bin/env python3
"""
Check SQLite database directly
"""
import sqlite3
import os

def check_sqlite_database():
    """Check the local SQLite database"""
    db_path = 'school_management'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("✅ SQLite database connected successfully")
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        
        print(f"\n📊 Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check schools
        school_tables = [table[0] for table in tables if 'school' in table[0].lower()]
        
        if 'core_school' in school_tables:
            cursor.execute("SELECT COUNT(*) FROM core_school;")
            school_count = cursor.fetchone()[0]
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
                    status = "✅ Active" if school[4] else "❌ Inactive"
                    print(f"  - {school[1]} ({school[2]}) - {school[3]} - {status}")
                    print(f"    ID: {school[0]}, Created: {school[5]}")
        
        # Check users
        if 'auth_user' in [table[0] for table in tables]:
            cursor.execute("SELECT COUNT(*) FROM auth_user;")
            user_count = cursor.fetchone()[0]
            print(f"\n👥 Users in database: {user_count}")
            
            if user_count > 0:
                cursor.execute("""
                    SELECT id, username, email, is_staff, is_superuser, date_joined 
                    FROM auth_user 
                    ORDER BY date_joined DESC 
                    LIMIT 10;
                """)
                users = cursor.fetchall()
                
                print("\n👤 Recent Users:")
                for user in users:
                    staff = "👨‍💼 Staff" if user[3] else "👤 User"
                    superuser = "🔧 Super" if user[4] else ""
                    print(f"  - {user[1]} ({user[2]}) - {staff} {superuser}")
                    print(f"    ID: {user[0]}, Joined: {user[5]}")
        
        # Check user profiles
        if 'accounts_userprofile' in [table[0] for table in tables]:
            cursor.execute("SELECT COUNT(*) FROM accounts_userprofile;")
            profile_count = cursor.fetchone()[0]
            print(f"\n👨‍💼 User Profiles: {profile_count}")
            
            if profile_count > 0:
                cursor.execute("""
                    SELECT up.id, u.username, up.role, up.employee_id, up.school_id
                    FROM accounts_userprofile up
                    JOIN auth_user u ON up.user_id = u.id
                    ORDER BY up.created_at DESC
                    LIMIT 10;
                """)
                profiles = cursor.fetchall()
                
                print("\n📇 User Profile Details:")
                for profile in profiles:
                    print(f"  - {profile[1]} - Role: {profile[2]}, Employee ID: {profile[3]}")
                    print(f"    Profile ID: {profile[0]}, School ID: {profile[4]}")
        
        # Check login logs
        if 'accounts_loginlog' in [table[0] for table in tables]:
            cursor.execute("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
                       COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                       COUNT(CASE WHEN status = 'blocked' THEN 1 END) as blocked
                FROM accounts_loginlog;
            """)
            login_stats = cursor.fetchone()
            
            print(f"\n🔐 Login Statistics:")
            print(f"  - Total attempts: {login_stats[0]}")
            print(f"  - Successful: {login_stats[1]}")
            print(f"  - Failed: {login_stats[2]}")
            print(f"  - Blocked: {login_stats[3]}")
            
            if login_stats[0] > 0:
                cursor.execute("""
                    SELECT username_attempted, status, ip_address, timestamp 
                    FROM accounts_loginlog 
                    ORDER BY timestamp DESC 
                    LIMIT 10;
                """)
                recent_logins = cursor.fetchall()
                
                print("\n📈 Recent Login Attempts:")
                for login in recent_logins:
                    status_icon = "✅" if login[1] == 'success' else "❌" if login[1] == 'failed' else "🚫"
                    print(f"  {status_icon} {login[0]} - {login[2]} - {login[3]}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_sqlite_database()
