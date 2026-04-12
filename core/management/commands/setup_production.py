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
            '--skip-school',
            action='store_true',
            help='Skip school configuration',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(' Setting up production environment...')
        )

        # REMOVED: Admin user creation - multi-tenant system uses school-specific admins
        # Create school configuration
        if not options['skip_school']:
            self.create_school_config()

        # REMOVED: Sample users creation for production
        self.stdout.write(
            self.style.SUCCESS(' Production setup completed successfully!')
        )

    def create_school_config(self):
        """Create school configuration if it doesn't exist - DISABLED for proper registration flow"""
        # Skip automatic school creation to allow proper registration
        self.stdout.write(
            self.style.SUCCESS(' Skipping automatic school setup - use registration page instead')
        )

    # REMOVED: create_admin_user method - no global admin in multi-tenant system
    # REMOVED: create_sample_users method - no fake data in production