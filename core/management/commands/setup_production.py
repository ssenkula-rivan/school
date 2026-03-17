"""
Management command to set up production environment
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile, SchoolConfiguration
import os


class Command(BaseCommand):
    help = 'Set up production environment with initial data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-admin',
            action='store_true',
            help='Skip admin user creation',
        )
        parser.add_argument(
            '--skip-school',
            action='store_true',
            help='Skip school configuration',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Setting up production environment...')
        )

        # Create admin user
        if not options['skip_admin']:
            self.create_admin_user()

        # Create school configuration
        if not options['skip_school']:
            self.create_school_config()

        # Create sample users
        self.create_sample_users()

        self.stdout.write(
            self.style.SUCCESS('✅ Production setup completed successfully!')
        )

    def create_admin_user(self):
        """Create admin user if it doesn't exist"""
        admin_password = os.environ.get('SYSADMIN_PASSWORD', 'SecureAdmin2024!')
        
        if not User.objects.filter(username='admin').exists():
            user = User.objects.create_superuser(
                username='admin',
                email='admin@school.com',
                password=admin_password,
                first_name='System',
                last_name='Administrator'
            )
            
            UserProfile.objects.create(
                user=user,
                employee_id='ADMIN001',
                role='admin',
                phone='+1-234-567-8900'
            )
            
            self.stdout.write(
                self.style.SUCCESS('✅ Admin user created: admin')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  Admin user already exists')
            )

    def create_school_config(self):
        """Create school configuration if it doesn't exist"""
        if not SchoolConfiguration.objects.exists():
            school = SchoolConfiguration.objects.create(
                school_name=os.environ.get('COMPANY_NAME', 'School Management System'),
                school_type='secondary',
                institution_type='private',
                address=os.environ.get('COMPANY_ADDRESS', 'School Address'),
                phone=os.environ.get('COMPANY_PHONE', '+1-234-567-8900'),
                email=os.environ.get('COMPANY_EMAIL', 'admin@school.com'),
                is_configured=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ School configured: {school.school_name}')
            )
        else:
            # Ensure existing school is marked as configured
            school = SchoolConfiguration.objects.first()
            if not school.is_configured:
                school.is_configured = True
                school.save()
                self.stdout.write(
                    self.style.SUCCESS('✅ School configuration updated')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️  School already configured')
                )

    def create_sample_users(self):
        """Create sample users for different roles"""
        users_to_create = [
            {
                'username': 'accountant',
                'email': 'accountant@school.com',
                'first_name': 'John',
                'last_name': 'Accountant',
                'role': 'accountant',
                'employee_id': 'ACC001'
            },
            {
                'username': 'teacher',
                'email': 'teacher@school.com',
                'first_name': 'Jane',
                'last_name': 'Teacher',
                'role': 'teacher',
                'employee_id': 'TCH001'
            },
            {
                'username': 'bursar',
                'email': 'bursar@school.com',
                'first_name': 'Bob',
                'last_name': 'Bursar',
                'role': 'bursar',
                'employee_id': 'BUR001'
            }
        ]

        password = os.environ.get('SYSADMIN_PASSWORD', 'SecureAdmin2024!')
        
        for user_data in users_to_create:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=password,
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                user.is_staff = True
                user.save()
                
                UserProfile.objects.create(
                    user=user,
                    employee_id=user_data['employee_id'],
                    role=user_data['role'],
                    phone='+1-234-567-8900'
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created {user_data["role"]}: {user_data["username"]}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  User {user_data["username"]} already exists')
                )

        self.stdout.write(
            self.style.SUCCESS(f'🔑 Default password for all users: {password}')
        )
        self.stdout.write(
            self.style.WARNING('⚠️  Change passwords after first login!')
        )