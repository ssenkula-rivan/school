from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from core.models import School, AcademicYear
from django.utils import timezone
from django.db import transaction


class Command(BaseCommand):
    help = 'Create a test school with admin account'

    def add_arguments(self, parser):
        parser.add_argument('--school-name', type=str, default='Test School', help='School name')
        parser.add_argument('--username', type=str, default='admin', help='Admin username')
        parser.add_argument('--password', type=str, default='admin123', help='Admin password')
        parser.add_argument('--email', type=str, default='admin@testschool.edu', help='Admin email')

    def handle(self, *args, **options):
        school_name = options['school_name']
        username = options['username']
        password = options['password']
        email = options['email']
        
        try:
            with transaction.atomic():
                if School.objects.filter(name=school_name).exists():
                    self.stdout.write(self.style.ERROR(f'School "{school_name}" already exists'))
                    return
                
                if User.objects.filter(username=username).exists():
                    self.stdout.write(self.style.ERROR(f'Username "{username}" already exists'))
                    return
                
                school_code = school_name.lower().replace(' ', '')[:15]
                base_code = school_code
                counter = 1
                while School.objects.filter(code=school_code).exists():
                    school_code = f"{base_code}{counter}"
                    counter += 1
                
                current_date = timezone.now().date()
                
                school = School.objects.create(
                    name=school_name,
                    code=school_code,
                    school_type='primary',
                    institution_type='private',
                    email=email,
                    email_domain=email.split('@')[1] if '@' in email else f'{school_code}.edu',
                    phone='+256700000000',
                    address='Test Address',
                    website='',
                    is_active=True,
                    subscription_start=current_date,
                    subscription_end=current_date.replace(year=current_date.year + 1),
                    max_students=1000,
                    max_staff=100,
                    currency='UGX',
                    timezone='Africa/Kampala',
                    has_primary=True,
                    is_private=True,
                    has_day=True,
                )
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name='Admin',
                    last_name='User',
                    is_staff=True,
                    is_active=True,
                )
                
                UserProfile.objects.create(
                    user=user,
                    school=school,
                    employee_id=f'ADM{user.id:04d}',
                    role='admin',
                    phone='+256700000000',
                    is_active_employee=True,
                )
                
                current_year = timezone.now().year
                AcademicYear.objects.create(
                    school=school,
                    name=f"{current_year}/{current_year + 1}",
                    start_date=current_date,
                    end_date=current_date.replace(year=current_date.year + 1),
                    is_current=True
                )
                
                self.stdout.write(self.style.SUCCESS(f'School "{school_name}" created successfully'))
                self.stdout.write(self.style.SUCCESS(f'Admin account created:'))
                self.stdout.write(f'  Username: {username}')
                self.stdout.write(f'  Password: {password}')
                self.stdout.write(f'  Email: {email}')
                self.stdout.write(f'  School Code: {school_code}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating school: {str(e)}'))
