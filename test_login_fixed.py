#!/usr/bin/env python3
"""
Test login functionality - fixed version
"""
import sqlite3
import os

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
            
            # Check user profile table structure first
            cursor.execute("PRAGMA table_info(accounts_userprofile);")
            profile_columns = cursor.fetchall()
            print(f"\n📋 UserProfile table columns:")
            for col in profile_columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Check if user has profile
            cursor.execute("""
                SELECT * FROM accounts_userprofile WHERE user_id = ?;
            """, (admin_user[0],))
            profile = cursor.fetchone()
            
            if profile:
                print(f"\n✅ User profile found:")
                for i, col in enumerate(profile_columns):
                    if i < len(profile):
                        print(f"  {col[1]}: {profile[i]}")
            else:
                print(f"\n❌ No user profile found for user ID {admin_user[0]}")
                print("💡 This is likely the login issue!")
                print("   Users need a UserProfile to login properly")
        else:
            print("❌ No admin user found")
        
        # Check all users
        cursor.execute("SELECT COUNT(*) FROM auth_user;")
        total_users = cursor.fetchone()[0]
        print(f"\n👥 Total users in database: {total_users}")
        
        # Check all profiles
        cursor.execute("SELECT COUNT(*) FROM accounts_userprofile;")
        total_profiles = cursor.fetchone()[0]
        print(f"👨‍💼 Total user profiles: {total_profiles}")
        
        # Check recent login attempts
        cursor.execute("SELECT COUNT(*) FROM accounts_loginlog;")
        login_attempts = cursor.fetchone()[0]
        print(f"🔐 Total login attempts: {login_attempts}")
        
        # Check school configuration
        cursor.execute("SELECT COUNT(*) FROM accounts_schoolconfiguration;")
        school_config = cursor.fetchone()[0]
        print(f"⚙️ School configurations: {school_config}")
        
        # Check Django sessions
        cursor.execute("SELECT COUNT(*) FROM django_session;")
        sessions = cursor.fetchone()[0]
        print(f"🌐 Active sessions: {sessions}")
        
        conn.close()
        
        # Summary and recommendations
        print("\n📊 SUMMARY:")
        print("=" * 20)
        print(f"Schools: 1 (Test School)")
        print(f"Users: {total_users}")
        print(f"User Profiles: {total_profiles}")
        print(f"Login Attempts: {login_attempts}")
        
        if total_users > total_profiles:
            print(f"\n⚠️  ISSUE DETECTED:")
            print(f"   {total_users - total_profiles} user(s) missing UserProfile")
            print("   This is likely causing the login failure!")
        
        print("\n💡 RECOMMENDATIONS:")
        print("1. Create missing UserProfile records")
        print("2. Check login form CSRF token")
        print("3. Verify authentication middleware")
        print("4. Test admin login at /admin/")
        print("5. Check browser console for JavaScript errors")
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login()
