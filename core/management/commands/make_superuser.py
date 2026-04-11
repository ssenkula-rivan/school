"""
Management command to make a user a Django superuser
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Make a user a Django superuser'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to make superuser')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully made {username} a superuser with staff access'
                )
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User {username} does not exist')
            )
