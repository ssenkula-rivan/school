from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Reset admin password for a school'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='Admin username')
        parser.add_argument('--password', type=str, required=True, help='New password')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        
        try:
            user = User.objects.get(username=username)
            
            try:
                profile = user.userprofile
                if profile.role != 'admin':
                    self.stdout.write(self.style.WARNING(f'User {username} is not an admin (role: {profile.role})'))
                    return
                
                user.set_password(password)
                user.save()
                
                self.stdout.write(self.style.SUCCESS(f'Password reset successfully for {username}'))
                self.stdout.write(f'School: {profile.school.name}')
                self.stdout.write(f'New password: {password}')
                
            except UserProfile.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User {username} has no profile'))
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} not found'))
