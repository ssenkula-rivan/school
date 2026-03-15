from django.core.management.base import BaseCommand
from core.backup import BackupManager

class Command(BaseCommand):
    help = 'Cleanup old backups'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Keep backups from last N days (default: 30)'
        )

    def handle(self, *args, **options):
        days = options['days']
        
        self.stdout.write(f'Cleaning up backups older than {days} days...')
        
        manager = BackupManager()
        manager.cleanup_old_backups(keep_days=days)
        
        self.stdout.write(
            self.style.SUCCESS('Cleanup completed')
        )
