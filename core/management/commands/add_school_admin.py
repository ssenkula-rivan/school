from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from core.models import School
from django.db import transaction


class Command(BaseCommand):
    help = 'Add admin account to an existing school'

    def add_arguments(self, parser):
        parser.add_argument('--school-code', type=str, required=True, help='School code')
        parser.add_argument('--username', type=str, required=True, help='Admin username')
        parser.add_argument('--password', type=str, required=True, help='Admin password')
        parser.add_argument('--email', type=str, required=True, help='Admin email')
        parser.add_argument('--first-name', type=str, default='Admin', help='First name')
        parser.add_argument('--last-name', type=str, default='User', help='Last name')
        parser.add_argument('--phone', type=str, default='', help='Phone number')

    def handle(self, *args, **options):
        school_code = options['school_code']
        username = options['username']
        password = options['password']
        email = options['email']
        first_name = options['first_name']
        last_name = options['last_name']
        phone = options['phone']
        
        try:
            with transaction.atomic():
                try:
                    school = School.objects.get(code=school_code)
                except School.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'School with code "{school_code}" not found'))
                    self.stdout.write('\nAvailable schools:')
                    for s in School.objects.all():
                        self.stdout.write(f'  - {s.name} (code: {s.code})')
                    return
                
                if User.objects.filter(username=username).exists():
                    self.stdout.write(self.style.ERROR(f'Username "{username}" already exists'))
                    return
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=True,
                    is_active=True,
                )
                
                UserProfile.objects.create(
                    user=user,
                    school=school,
                    employee_id=f'ADM{user.id:04d}',
                    role='admin',
                    phone=phone,
                    is_active_employee=True,
                )
                
                self.stdout.write(self.style.SUCCESS(f'\nAdmin account created successfully!'))
                self.stdout.write(f'School: {school.name}')
                self.stdout.write(f'Username: {username}')
                self.stdout.write(f'Password: {password}')
                self.stdout.write(f'Email: {email}')
                self.stdout.write(f'\nLogin at: https://school-management-system-bwfu.onrender.com/accounts/login/')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating admin: {str(e)}'))
