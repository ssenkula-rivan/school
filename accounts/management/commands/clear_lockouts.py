from django.core.management.base import BaseCommand
from axes.models import AccessAttempt
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Clear all account lockouts and reset failed login attempts'

    def handle(self, *args, **options):
        # Clear all access attempts
        attempts_count = AccessAttempt.objects.count()
        AccessAttempt.objects.all().delete()
        
        # Reset user lockout flags (if any)
        users_updated = 0
        for user in User.objects.all():
            if hasattr(user, 'is_locked') and user.is_locked:
                user.is_locked = False
                user.save()
                users_updated += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f' Cleared {attempts_count} failed login attempts and unlocked {users_updated} users'
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS(' All accounts are now unlocked and can login normally')
        )
