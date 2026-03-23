#!/usr/bin/env python3
"""
Create UserProfile for admin user
"""
import sqlite3
import os
import uuid
from datetime import datetime, date

def create_profile():
    """Create UserProfile for admin user"""
    db_path = 'school_management'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Creating UserProfile for Admin")
        print("=" * 40)
        
        # Get admin user
        cursor.execute("SELECT id, username FROM auth_user WHERE username = 'admin';")
        admin_user = cursor.fetchone()
        
        if not admin_user:
            print("❌ No admin user found")
            return
        
        user_id = admin_user[0]
        print(f"✅ Found admin user: {admin_user[1]} (ID: {user_id})")
        
        # Create UserProfile
        employee_id = f"EMP-{uuid.uuid4().hex[:8].upper()}"
        today = date.today()
        now = datetime.now()
        
        cursor.execute("""
            INSERT INTO accounts_userprofile 
            (employee_id, role, phone, address, hire_date, is_active_employee, created_at, updated_at, department_id, user_id, class_name, force_password_reset)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            employee_id,      # employee_id
            'admin',         # role
            '',              # phone
            '',              # address
            today,           # hire_date
            1,               # is_active_employee (as integer)
            now,             # created_at
            now,             # updated_at
            None,            # department_id
            user_id,         # user_id
            '',              # class_name
            0                # force_password_reset (as integer)
        ))
        
        profile_id = cursor.lastrowid
        print(f"✅ Created UserProfile with ID: {profile_id}")
        print(f"  Employee ID: {employee_id}")
        
        # Update user to be staff and superuser
        cursor.execute("UPDATE auth_user SET is_staff = 1, is_superuser = 1 WHERE id = ?;", (user_id,))
        print("✅ Updated user to staff and superuser")
        
        # Commit the transaction
        conn.commit()
        
        # Verify creation
        cursor.execute("SELECT COUNT(*) FROM accounts_userprofile;")
        profile_count = cursor.fetchone()[0]
        print(f"✅ Total UserProfiles now: {profile_count}")
        
        conn.close()
        
        print("\n🎉 SUCCESS!")
        print("=" * 20)
        print("✅ UserProfile created for admin user")
        print("✅ User updated to staff and superuser")
        
        print("\n🔑 LOGIN INFO:")
        print("URL: https://school-management-c-8qtq.onrender.com/accounts/login/")
        print("Username: admin")
        print("Password: [Your existing admin password]")
        
        print("\n💡 If password doesn't work:")
        print("1. Use password reset feature")
        print("2. Or access Django admin at /admin/")
        print("3. Create a new superuser if needed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()

if __name__ == "__main__":
    create_profile()
