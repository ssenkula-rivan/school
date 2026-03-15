from django.core.management.base import BaseCommand
from core.backup import BackupManager

class Command(BaseCommand):
    help = 'Create database backup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='manual',
            help='Backup type (auto, manual, daily)'
        )

    def handle(self, *args, **options):
        backup_type = options['type']
        
        self.stdout.write('Creating database backup...')
        
        manager = BackupManager()
        backup_path = manager.create_backup(backup_type)
        
        if backup_path:
            self.stdout.write(
                self.style.SUCCESS(f'Backup created: {backup_path}')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Backup failed')
            )
