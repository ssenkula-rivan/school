"""
Management command to reset school configuration for proper setup
"""
from django.core.management.base import BaseCommand
from accounts.models import SchoolConfiguration


class Command(BaseCommand):
    help = 'Reset school configuration to allow proper school registration'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(' Resetting school configuration...')
        )

        # Delete existing school configuration
        deleted_count = SchoolConfiguration.objects.all().delete()[0]
        
        if deleted_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f' Deleted {deleted_count} school configuration(s)')
            )
        else:
            self.stdout.write(
                self.style.WARNING('  No school configuration found to delete')
            )

        self.stdout.write(
            self.style.SUCCESS(' School configuration reset completed!')
        )
        self.stdout.write(
            self.style.SUCCESS(' Now visit your site to see the school registration page')
        )