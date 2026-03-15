#!/usr/bin/env python3
"""
School Management System - Installation Wizard

USAGE:
    python3 scripts/installation/install_wizard.py

This wizard will:
1. Configure database (SQLite/PostgreSQL/MySQL)
2. Create environment configuration
3. Run database migrations
4. Create admin account
5. Collect static files
6. Create desktop shortcut

Allows admin to choose between existing database or new database
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header():
    print("\n" + "="*60)
    print("SCHOOL MANAGEMENT SYSTEM - INSTALLATION WIZARD")
    print("="*60 + "\n")

def print_step(step_num, title):
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {title}")
    print(f"{'='*60}\n")

def get_choice(prompt, options):
    """Get user choice from options"""
    print(prompt)
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (number): "))
            if 1 <= choice <= len(options):
                return choice
            print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("Please enter a valid number")

def get_input(prompt, default=None):
    """Get user input with optional default"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()

def test_database_connection(db_type, config):
    """Test database connection"""
    print("\nTesting database connection...")
    
    if db_type == 'postgresql':
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                database=config['name'],
                user=config['user'],
                password=config['password']
            )
            conn.close()
            print("✓ Database connection successful!")
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {str(e)}")
            return False
    
    elif db_type == 'mysql':
        try:
            import pymysql
            conn = pymysql.connect(
                host=config['host'],
                port=int(config['port']),
                database=config['name'],
                user=config['user'],
                password=config['password']
            )
            conn.close()
            print("✓ Database connection successful!")
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {str(e)}")
            return False
    
    return True

def configure_database():
    """Configure database settings"""
    print_step(1, "DATABASE CONFIGURATION")
    
    db_choice = get_choice(
        "Choose your database option:",
        [
            "Use SQLite (Simple, no setup required - Recommended for testing)",
            "Use existing PostgreSQL database",
            "Use existing MySQL database"
        ]
    )
    
    if db_choice == 1:
        # SQLite
        print("\n✓ Using SQLite database (db.sqlite3)")
        return {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3'
        }
    
    elif db_choice == 2:
        # PostgreSQL
        print("\nConfiguring PostgreSQL connection...")
        config = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': get_input("Database name", "school_db"),
            'USER': get_input("Database user", "postgres"),
            'PASSWORD': get_input("Database password"),
            'HOST': get_input("Database host", "localhost"),
            'PORT': get_input("Database port", "5432")
        }
        
        if test_database_connection('postgresql', config):
            return config
        else:
            retry = input("\nRetry configuration? (y/n): ").lower()
            if retry == 'y':
                return configure_database()
            sys.exit(1)
    
    elif db_choice == 3:
        # MySQL
        print("\nConfiguring MySQL connection...")
        config = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': get_input("Database name", "school_db"),
            'USER': get_input("Database user", "root"),
            'PASSWORD': get_input("Database password"),
            'HOST': get_input("Database host", "localhost"),
            'PORT': get_input("Database port", "3306")
        }
        
        if test_database_connection('mysql', config):
            return config
        else:
            retry = input("\nRetry configuration? (y/n): ").lower()
            if retry == 'y':
                return configure_database()
            sys.exit(1)

def update_settings_file(db_config):
    """Update Django settings with database configuration"""
    print("\nUpdating settings.py...")
    
    # Get project root (2 levels up from this script)
    project_root = Path(__file__).parent.parent.parent
    settings_path = project_root / 'workplace_system' / 'settings.py'
    
    if not settings_path.exists():
        print("✗ settings.py not found!")
        return False
    
    # Create database configuration string
    db_config_str = "DATABASES = {\n    'default': {\n"
    for key, value in db_config.items():
        if key == 'NAME' and db_config['ENGINE'] == 'django.db.backends.sqlite3':
            db_config_str += f"        '{key}': BASE_DIR / '{value}',\n"
        else:
            db_config_str += f"        '{key}': '{value}',\n"
    db_config_str += "    }\n}"
    
    # Read current settings
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # Replace DATABASES configuration
    import re
    pattern = r'DATABASES\s*=\s*\{[^}]*\{[^}]*\}[^}]*\}'
    if re.search(pattern, content):
        content = re.sub(pattern, db_config_str, content)
    else:
        print("✗ Could not find DATABASES configuration in settings.py")
        return False
    
    # Write updated settings
    with open(settings_path, 'w') as f:
        f.write(content)
    
    print("✓ Settings updated successfully!")
    return True

def create_env_file():
    """Create .env file with configuration"""
    print_step(2, "ENVIRONMENT CONFIGURATION")
    
    # Get project root (2 levels up from this script)
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / '.env'
    
    print("\nConfiguring environment variables...")
    
    secret_key = get_input("Django SECRET_KEY (leave blank to generate)", "")
    if not secret_key:
        import secrets
        secret_key = secrets.token_urlsafe(50)
        print(f"Generated SECRET_KEY: {secret_key[:20]}...")
    
    debug = get_choice("Enable DEBUG mode?", ["Yes (Development)", "No (Production)"])
    debug_value = "True" if debug == 1 else "False"
    
    allowed_hosts = get_input("ALLOWED_HOSTS (comma-separated)", "localhost,127.0.0.1")
    
    env_content = f"""# Django Configuration
SECRET_KEY={secret_key}
DEBUG={debug_value}
ALLOWED_HOSTS={allowed_hosts}

# Email Configuration (Optional - for password reset)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# System Admin Password (Optional)
SYSADMIN_PASSWORD=
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("✓ .env file created successfully!")

def run_migrations():
    """Run database migrations"""
    print_step(3, "DATABASE SETUP")
    
    print("\nRunning database migrations...")
    
    # Get project root (2 levels up from this script)
    project_root = Path(__file__).parent.parent.parent
    
    try:
        result = subprocess.run(
            ['python3', 'manage.py', 'migrate'],
            capture_output=True,
            text=True,
            cwd=str(project_root)
        )
        
        if result.returncode == 0:
            print("✓ Database migrations completed successfully!")
            return True
        else:
            print(f"✗ Migration failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error running migrations: {str(e)}")
        return False

def create_superuser():
    """Create initial superuser"""
    print_step(4, "ADMIN ACCOUNT SETUP")
    
    print("\nYou can create the admin account now or later.")
    create_now = get_choice("Create admin account now?", ["Yes", "No, I'll do it later"])
    
    if create_now == 1:
        print("\nCreating superuser account...")
        print("(You'll be prompted for username, email, and password)")
        
        # Get project root (2 levels up from this script)
        project_root = Path(__file__).parent.parent.parent
        
        try:
            subprocess.run(['python3', 'manage.py', 'createsuperuser'], cwd=str(project_root))
            print("\n✓ Superuser created successfully!")
        except Exception as e:
            print(f"\n✗ Error creating superuser: {str(e)}")
            print("You can create it later using: python3 manage.py createsuperuser")
    else:
        print("\nYou can create the admin account later using:")
        print("  python3 manage.py createsuperuser")

def collect_static():
    """Collect static files"""
    print("\nCollecting static files...")
    
    # Get project root (2 levels up from this script)
    project_root = Path(__file__).parent.parent.parent
    
    try:
        result = subprocess.run(
            ['python3', 'manage.py', 'collectstatic', '--noinput'],
            capture_output=True,
            text=True,
            cwd=str(project_root)
        )
        
        if result.returncode == 0:
            print("✓ Static files collected successfully!")
            return True
        else:
            print(f"✗ Static collection failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error collecting static files: {str(e)}")
        return False

def create_desktop_shortcut():
    """Create desktop shortcut"""
    print_step(5, "DESKTOP SHORTCUT")
    
    create = get_choice("Create desktop shortcut?", ["Yes", "No"])
    
    if create == 1:
        print("\nCreating desktop shortcut...")
        # Get path to create_shortcut.py in same directory
        shortcut_script = Path(__file__).parent / 'create_shortcut.py'
        try:
            subprocess.run([sys.executable, str(shortcut_script)])
            print("✓ Desktop shortcut created!")
        except Exception as e:
            print(f"✗ Could not create shortcut: {e}")
            print("You can create it later by running: python3 create_shortcut.py")

def print_completion():
    """Print installation completion message"""
    print("\n" + "="*60)
    print("INSTALLATION COMPLETED SUCCESSFULLY!")
    print("="*60)
    
    print("\nNext steps:")
    print("  1. Double-click the desktop icon to launch the system")
    print("     OR run: python3 launcher.py")
    print("\n  2. Register your school:")
    print("     http://localhost:8000/accounts/register-school/")
    print("\n  3. Login with your admin account")
    
    print("\n" + "="*60)
    print("Thank you for installing School Management System!")
    print("="*60 + "\n")

def main():
    """Main installation wizard"""
    print_header()
    
    print("Welcome to the School Management System Installation Wizard!")
    print("This wizard will help you set up your system.\n")
    
    input("Press Enter to continue...")
    
    # Step 1: Configure database
    db_config = configure_database()
    
    # Step 2: Update settings file
    if not update_settings_file(db_config):
        print("\n✗ Installation failed!")
        sys.exit(1)
    
    # Step 3: Create .env file
    create_env_file()
    
    # Step 4: Run migrations
    if not run_migrations():
        print("\n✗ Installation failed!")
        sys.exit(1)
    
    # Step 5: Collect static files
    collect_static()
    
    # Step 6: Create superuser
    create_superuser()
    
    # Step 7: Create desktop shortcut
    create_desktop_shortcut()
    
    # Print completion message
    print_completion()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Installation failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
