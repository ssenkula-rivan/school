"""
Management command to generate secure keys
"""
from django.core.management.base import BaseCommand
from workplace_system.security import SecureKeyGenerator


class Command(BaseCommand):
    help = 'Generate secure keys for the application'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='secret_key',
            choices=['secret_key', 'api_key', 'token', 'password'],
            help='Type of key to generate'
        )
        parser.add_argument(
            '--length',
            type=int,
            default=32,
            help='Length of the key (for api_key and token)'
        )
    
    def handle(self, *args, **options):
        key_type = options['type']
        length = options['length']
        
        if key_type == 'secret_key':
            key = SecureKeyGenerator.generate_secret_key()
            self.stdout.write(self.style.SUCCESS('Generated SECRET_KEY:'))
            self.stdout.write(self.style.WARNING(key))
            self.stdout.write('\nAdd this to your .env file:')
            self.stdout.write(self.style.WARNING(f'SECRET_KEY={key}'))
        
        elif key_type == 'api_key':
            key = SecureKeyGenerator.generate_api_key(length)
            self.stdout.write(self.style.SUCCESS(f'Generated API Key ({length} chars):'))
            self.stdout.write(self.style.WARNING(key))
        
        elif key_type == 'token':
            key = SecureKeyGenerator.generate_token(length)
            self.stdout.write(self.style.SUCCESS(f'Generated Token ({length} chars):'))
            self.stdout.write(self.style.WARNING(key))
        
        elif key_type == 'password':
            key = SecureKeyGenerator.generate_password(length)
            self.stdout.write(self.style.SUCCESS(f'Generated Password ({length} chars):'))
            self.stdout.write(self.style.WARNING(key))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Key generated successfully'))
