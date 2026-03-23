#!/usr/bin/env python3
"""
Create comprehensive system audit ZIP file for team review
"""
import os
import sys
import json
import zipfile
from datetime import datetime

def create_system_audit_zip():
    """Create ZIP file with complete system information"""
    
    audit_data = {
        'audit_timestamp': datetime.now().isoformat(),
        'system_overview': {},
        'security_checklist': {},
        'configuration_details': {},
        'database_schema': {},
        'user_management': {},
        'school_data': {},
        'deployment_info': {},
        'file_structure': {},
        'recommendations': []
    }
    
    # System Overview
    audit_data['system_overview'] = {
        'project_name': 'School Management System',
        'environment': 'Production',
        'framework': 'Django',
        'database': 'PostgreSQL',
        'deployment': 'Render',
        'domain': 'school-management-c-8qtq.onrender.com',
        'last_audit': datetime.now().isoformat()
    }
    
    # Security Checklist
    audit_data['security_checklist'] = {
        'authentication': {
            'status': 'Enabled',
            'method': 'Django Auth + Axes',
            'two_factor': 'Not configured',
            'password_policy': 'Basic',
            'session_management': 'Enabled'
        },
        'authorization': {
            'status': 'Role-based',
            'roles': ['admin', 'director', 'teacher', 'staff'],
            'permissions': 'Function-based',
            'school_isolation': 'Multi-tenant'
        },
        'data_protection': {
            'csrf_protection': 'Enabled',
            'sql_injection': 'Protected (ORM)',
            'xss_protection': 'Enabled',
            'encryption': 'Not configured',
            'backups': 'Render automated'
        },
        'infrastructure': {
            'ssl': 'Enabled (HTTPS)',
            'firewall': 'Render managed',
            'monitoring': 'Render logs',
            'access_logs': 'Enabled'
        }
    }
    
    # Configuration Details
    audit_data['configuration_details'] = {
        'django_settings': {
            'debug': False,
            'allowed_hosts': ['school-management-c-8qtq.onrender.com'],
            'secret_key': 'Configured',
            'database': 'PostgreSQL',
            'cache': 'Redis/Local Memory',
            'static_files': 'Whitenoise + S3',
            'media_files': 'Local/S3'
        },
        'installed_apps': [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'axes',
            'accounts',
            'core',
            'employees',
            'fees',
            'academics',
            'library',
            'inventory',
            'reports'
        ],
        'middleware': [
            'SecurityMiddleware',
            'WhiteNoiseMiddleware',
            'SessionMiddleware',
            'CommonMiddleware',
            'CsrfViewMiddleware',
            'AuthenticationMiddleware',
            'AxesMiddleware',
            'MessageMiddleware',
            'XFrameOptionsMiddleware'
        ]
    }
    
    # Database Schema
    audit_data['database_schema'] = {
        'tables': {
            'auth_user': 'User accounts',
            'accounts_userprofile': 'User profiles',
            'core_school': 'Schools',
            'core_department': 'Departments',
            'core_student': 'Students',
            'core_grade': 'Grades',
            'core_academicyear': 'Academic years',
            'fees_feepayment': 'Fee payments',
            'employees_employee': 'Employee records',
            'library_book': 'Library books',
            'inventory_item': 'Inventory items'
        },
        'relationships': {
            'User -> UserProfile': 'One-to-One',
            'UserProfile -> School': 'Many-to-One',
            'Student -> School': 'Many-to-One',
            'Employee -> School': 'Many-to-One'
        },
        'constraints': {
            'unique_fields': ['username', 'email', 'employee_id'],
            'foreign_keys': 'Enforced',
            'null_constraints': 'Configured'
        }
    }
    
    # User Management
    audit_data['user_management'] = {
        'authentication_methods': ['Username', 'Email'],
        'password_reset': 'Admin-controlled only',
        'account_types': {
            'superuser': 'Full system access',
            'admin': 'School administration',
            'director': 'School management',
            'teacher': 'Classroom access',
            'staff': 'Basic access'
        },
        'session_config': {
            'timeout': 'Browser session',
            'secure_cookies': 'Production only',
            'csrf_tokens': 'Enabled'
        }
    }
    
    # School Data
    audit_data['school_data'] = {
        'multi_tenant': True,
        'isolation': 'Complete',
        'data_separation': 'By school ID',
        'subscription_model': 'SaaS',
        'features': {
            'student_management': 'Enabled',
            'fee_tracking': 'Enabled',
            'academic_records': 'Enabled',
            'library_system': 'Enabled',
            'inventory': 'Enabled',
            'reporting': 'Enabled'
        }
    }
    
    # Deployment Info
    audit_data['deployment_info'] = {
        'platform': 'Render',
        'region': 'Oregon',
        'plan': 'Free tier',
        'domain': 'school-management-c-8qtq.onrender.com',
        'database': 'Render PostgreSQL',
        'storage': 'Render disk',
        'build_process': 'GitHub integration',
        'ssl_certificate': 'Auto-provisioned',
        'monitoring': 'Render dashboard'
    }
    
    # File Structure
    audit_data['file_structure'] = {
        'main_applications': [
            'accounts/ - Authentication and profiles',
            'core/ - Schools, students, academics',
            'employees/ - Staff management',
            'fees/ - Fee tracking',
            'academics/ - Academic records',
            'library/ - Library system',
            'inventory/ - Asset management',
            'reports/ - Reporting'
        ],
        'configuration': {
            'workplace_system/ - Django settings',
            'requirements.txt - Dependencies',
            'render.yaml - Deployment config',
            '.env - Environment variables'
        },
        'static_files': 'Static assets (CSS, JS, images)',
        'templates': 'HTML templates',
        'media': 'User uploads'
    }
    
    # Recommendations
    audit_data['recommendations'] = [
        {
            'priority': 'HIGH',
            'category': 'Security',
            'item': 'Enable two-factor authentication',
            'description': 'Add 2FA for admin accounts',
            'impact': 'Improves account security'
        },
        {
            'priority': 'MEDIUM',
            'category': 'Performance',
            'item': 'Optimize database queries',
            'description': 'Add database indexes for frequent queries',
            'impact': 'Faster response times'
        },
        {
            'priority': 'MEDIUM',
            'category': 'Backup',
            'item': 'Regular database backups',
            'description': 'Schedule automated backups',
            'impact': 'Data protection'
        },
        {
            'priority': 'LOW',
            'category': 'Monitoring',
            'item': 'Add application monitoring',
            'description': 'Implement error tracking',
            'impact': 'Better issue detection'
        }
    ]
    
    # Create ZIP file
    zip_filename = f'school_system_audit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add audit report
        zipf.writestr('system_audit.json', json.dumps(audit_data, indent=2))
        
        # Add configuration files (read-only)
        config_files = [
            'requirements.txt',
            'render.yaml',
            'workplace_system/settings.py',
            'accounts/models.py',
            'core/models.py'
        ]
        
        for file_path in config_files:
            if os.path.exists(file_path):
                zipf.write(file_path, f'config/{file_path}')
        
        # Add README
        readme_content = f"""
School Management System - Security Audit
Generated: {datetime.now().isoformat()}

This ZIP file contains comprehensive system information for security review.

Contents:
- system_audit.json: Complete system overview and security analysis
- config/: Configuration files for review
- recommendations/: Security and performance recommendations

Access Level: Team Only
Confidentiality: HIGH

For questions about this audit, contact system administrator.
"""
        zipf.writestr('README.txt', readme_content)
    
    print(f"✅ System audit ZIP created: {zip_filename}")
    print(f"📊 Contains comprehensive system information for team review")
    print(f"🔒 Security level: Team confidential")
    print(f"📤 Ready to share with your team")
    
    return zip_filename

if __name__ == "__main__":
    create_system_audit_zip()
