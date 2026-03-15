"""
Suspend expired subscriptions - Run daily via cron
"""
from django.core.management.base import BaseCommand
from subscriptions.services import SubscriptionService


class Command(BaseCommand):
    help = 'Suspend expired subscriptions'
    
    def handle(self, *args, **options):
        count = SubscriptionService.suspend_expired_subscriptions()
        
        self.stdout.write(
            self.style.SUCCESS(f'Suspended {count} expired subscriptions')
        )
