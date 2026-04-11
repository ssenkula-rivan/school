from django.core.management.base import BaseCommand
from core.models import School
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'List all schools and their admin accounts'

    def handle(self, *args, **options):
        schools = School.objects.all()
        
        if not schools.exists():
            self.stdout.write(self.style.WARNING('No schools found'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'\nFound {schools.count()} school(s):\n'))
        
        for school in schools:
            self.stdout.write(f'\nSchool: {school.name}')
            self.stdout.write(f'Code: {school.code}')
            self.stdout.write(f'Email: {school.email}')
            self.stdout.write(f'Active: {school.is_active}')
            
            admins = UserProfile.objects.filter(school=school, role='admin').select_related('user')
            
            if admins.exists():
                self.stdout.write(self.style.SUCCESS(f'\nAdmin Accounts ({admins.count()}):'))
                for profile in admins:
                    user = profile.user
                    self.stdout.write(f'  Username: {user.username}')
                    self.stdout.write(f'  Email: {user.email}')
                    self.stdout.write(f'  Name: {user.first_name} {user.last_name}')
                    self.stdout.write(f'  Active: {user.is_active}')
            else:
                self.stdout.write(self.style.WARNING('  No admin accounts found'))
            
            self.stdout.write('-' * 60)
