"""
Create default subscription plans
"""
from django.core.management.base import BaseCommand
from subscriptions.models import Plan


class Command(BaseCommand):
    help = 'Create default subscription plans'
    
    def handle(self, *args, **options):
        plans_data = [
            {
                'name': 'Trial',
                'slug': 'trial',
                'description': '14-day free trial with limited features',
                'price': 0,
                'billing_cycle': 'monthly',
                'max_students': 50,
                'max_teachers': 5,
                'max_staff': 10,
                'max_storage_gb': 1,
                'trial_days': 14,
                'feature_flags': {
                    'advanced_reports': False,
                    'sms_integration': False,
                    'bulk_export': False,
                    'api_access': False,
                    'custom_branding': False,
                    'priority_support': False,
                },
                'is_public': False,
                'sort_order': 0,
            },
            {
                'name': 'Basic',
                'slug': 'basic',
                'description': 'Perfect for small schools',
                'price': 49.99,
                'billing_cycle': 'monthly',
                'max_students': 100,
                'max_teachers': 10,
                'max_staff': 20,
                'max_storage_gb': 5,
                'trial_days': 14,
                'feature_flags': {
                    'advanced_reports': False,
                    'sms_integration': False,
                    'bulk_export': True,
                    'api_access': False,
                    'custom_branding': False,
                    'priority_support': False,
                },
                'is_public': True,
                'sort_order': 1,
            },
            {
                'name': 'Professional',
                'slug': 'professional',
                'description': 'For growing schools',
                'price': 99.99,
                'billing_cycle': 'monthly',
                'max_students': 500,
                'max_teachers': 50,
                'max_staff': 100,
                'max_storage_gb': 20,
                'trial_days': 14,
                'feature_flags': {
                    'advanced_reports': True,
                    'sms_integration': True,
                    'bulk_export': True,
                    'api_access': False,
                    'custom_branding': False,
                    'priority_support': True,
                },
                'is_public': True,
                'sort_order': 2,
            },
            {
                'name': 'Enterprise',
                'slug': 'enterprise',
                'description': 'For large institutions',
                'price': 299.99,
                'billing_cycle': 'monthly',
                'max_students': 5000,
                'max_teachers': 500,
                'max_staff': 1000,
                'max_storage_gb': 100,
                'trial_days': 14,
                'feature_flags': {
                    'advanced_reports': True,
                    'sms_integration': True,
                    'bulk_export': True,
                    'api_access': True,
                    'custom_branding': True,
                    'priority_support': True,
                },
                'is_public': True,
                'sort_order': 3,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for plan_data in plans_data:
            plan, created = Plan.objects.update_or_create(
                slug=plan_data['slug'],
                defaults=plan_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created plan: {plan.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated plan: {plan.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone! Created: {created_count}, Updated: {updated_count}'
            )
        )
