#!/usr/bin/env python3
"""
Test login functionality
"""
import sqlite3
import os
import hashlib

def test_login():
    """Test login with existing user"""
    db_path = 'school_management'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔐 Testing Login Functionality")
        print("=" * 40)
        
        # Check the admin user
        cursor.execute("""
            SELECT id, username, email, password, is_staff, is_superuser, is_active
            FROM auth_user 
            WHERE username = 'admin';
        """)
        admin_user = cursor.fetchone()
        
        if admin_user:
            print(f"✅ Found admin user:")
            print(f"  Username: {admin_user[1]}")
            print(f"  Email: {admin_user[2]}")
            print(f"  Staff: {admin_user[4]}")
            print(f"  Superuser: {admin_user[5]}")
            print(f"  Active: {admin_user[6]}")
            print(f"  Password hash: {admin_user[3][:50]}...")
            
            # Check if user has profile
            cursor.execute("""
                SELECT up.id, up.role, up.employee_id, up.school_id
                FROM accounts_userprofile up
                WHERE up.user_id = ?;
            """, (admin_user[0],))
            profile = cursor.fetchone()
            
            if profile:
                print(f"✅ User profile found:")
                print(f"  Role: {profile[1]}")
                print(f"  Employee ID: {profile[2]}")
                print(f"  School ID: {profile[3]}")
            else:
                print("❌ No user profile found - this might be the login issue!")
                print("💡 Users need a UserProfile to login properly")
        else:
            print("❌ No admin user found")
        
        # Check authentication backend configuration
        print("\n🔧 Authentication Configuration:")
        print("  - Default Django auth backend")
        print("  - Axes backend for brute force protection")
        
        # Check Axes configuration
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%axes%';")
        axes_tables = cursor.fetchall()
        
        if axes_tables:
            print(f"✅ Axes tables found: {[t[0] for t in axes_tables]}")
        else:
            print("❌ No Axes tables found - brute force protection may not work")
        
        # Check recent login attempts
        cursor.execute("""
            SELECT COUNT(*) FROM accounts_loginlog;
        """)
        login_attempts = cursor.fetchone()[0]
        
        print(f"\n📊 Login attempts recorded: {login_attempts}")
        
        if login_attempts == 0:
            print("💡 No login attempts recorded - this suggests:")
            print("   1. Login form might not be working")
            print("   2. Authentication middleware misconfigured")
            print("   3. CSRF or session issues")
        
        # Check school configuration
        cursor.execute("""
            SELECT COUNT(*) FROM accounts_schoolconfiguration;
        """)
        school_config = cursor.fetchone()[0]
        
        print(f"\n⚙️ School configurations: {school_config}")
        
        if school_config == 0:
            print("❌ No school configuration found - this might prevent login!")
        
        conn.close()
        
        # Provide debugging steps
        print("\n🐛 Debugging Steps:")
        print("1. Try accessing: https://school-management-c-8qtq.onrender.com/admin/")
        print("2. Use username: admin")
        print("3. Check if password reset works")
        print("4. Look for error messages in browser console")
        print("5. Check network tab for failed requests")
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login()
