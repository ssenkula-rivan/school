from django.core.management.base import BaseCommand
from core.sync_manager import SyncManager

class Command(BaseCommand):
    help = 'Sync data with server when online'

    def add_arguments(self, parser):
        parser.add_argument(
            '--direction',
            type=str,
            default='both',
            choices=['push', 'pull', 'both'],
            help='Sync direction: push (to server), pull (from server), or both'
        )

    def handle(self, *args, **options):
        direction = options['direction']
        manager = SyncManager()
        
        self.stdout.write('Checking connection...')
        
        if not manager.is_online():
            self.stdout.write(
                self.style.WARNING('System is offline. Changes queued for later sync.')
            )
            status = manager.get_sync_status()
            self.stdout.write(f"Pending changes: {status['pending_changes']}")
            return
        
        self.stdout.write(self.style.SUCCESS('Online - Starting sync...'))
        
        if direction in ['push', 'both']:
            self.stdout.write('Pushing local changes to server...')
            result = manager.sync_to_server()
            self.stdout.write(
                self.style.SUCCESS(f"Synced {result['synced']} changes")
            )
            if result.get('errors'):
                for error in result['errors']:
                    self.stdout.write(self.style.ERROR(f"  {error}"))
        
        if direction in ['pull', 'both']:
            self.stdout.write('Pulling changes from server...')
            result = manager.sync_from_server()
            if result['status'] == 'success':
                self.stdout.write(
                    self.style.SUCCESS(f"Pulled {result['pulled']} changes")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"Pull failed: {result.get('message', 'Unknown error')}")
                )
        
        self.stdout.write(self.style.SUCCESS('Sync completed'))
