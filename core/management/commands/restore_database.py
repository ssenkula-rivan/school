from django.core.management.base import BaseCommand
from core.backup import BackupManager

class Command(BaseCommand):
    help = 'Restore database from backup'

    def add_arguments(self, parser):
        parser.add_argument(
            'backup_name',
            type=str,
            help='Name of backup to restore'
        )

    def handle(self, *args, **options):
        backup_name = options['backup_name']
        
        self.stdout.write(f'Restoring backup: {backup_name}')
        self.stdout.write(self.style.WARNING('This will overwrite current database!'))
        
        confirm = input('Type "yes" to continue: ')
        
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.ERROR('Restore cancelled'))
            return
        
        manager = BackupManager()
        
        try:
            manager.restore_backup(backup_name)
            self.stdout.write(
                self.style.SUCCESS('Database restored successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Restore failed: {str(e)}')
            )
