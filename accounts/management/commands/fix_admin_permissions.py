from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Fix permissions for all school admin users'

    def handle(self, *args, **options):
        # Make all users with role=admin or role=system_admin into staff
        admin_profiles = UserProfile.objects.filter(
            role__in=['admin', 'system_admin', 'director']
        ).select_related('user')

        count = 0
        for profile in admin_profiles:
            user = profile.user
            if not user.is_staff:
                user.is_staff = True
                user.save(update_fields=['is_staff'])
                count += 1
                self.stdout.write(f'Fixed: {user.username} (role={profile.role})')

        # Always fix rivan specifically as system owner
        try:
            rivan = User.objects.get(username='rivan')
            rivan.is_staff = True
            rivan.is_superuser = True
            rivan.save()
            self.stdout.write(self.style.SUCCESS('Fixed system owner: rivan'))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('User "rivan" not found'))

        self.stdout.write(
            self.style.SUCCESS(f'Done. Fixed {count} admin users.')
        )
