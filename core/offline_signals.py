from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.serializers import serialize
from core.sync_manager import SyncManager
import json

sync_manager = SyncManager()

def queue_model_change(sender, instance, action):
    """Queue model changes for sync"""
    if not sync_manager.is_online():
        model_name = f"{instance._meta.app_label}.{instance._meta.model_name}"
        
        # Serialize instance data
        data = json.loads(serialize('json', [instance]))[0]['fields']
        data['id'] = instance.pk
        
        sync_manager.queue_change(
            model_name=model_name,
            action=action,
            data=data,
            record_id=instance.pk
        )

@receiver(post_save)
def track_save(sender, instance, created, **kwargs):
    """Track create/update operations"""
    # Skip if model is in excluded list
    excluded_models = ['LogEntry', 'Session', 'ContentType']
    if sender.__name__ in excluded_models:
        return
    
    action = 'create' if created else 'update'
    queue_model_change(sender, instance, action)

@receiver(post_delete)
def track_delete(sender, instance, **kwargs):
    """Track delete operations"""
    # Skip if model is in excluded list
    excluded_models = ['LogEntry', 'Session', 'ContentType']
    if sender.__name__ in excluded_models:
        return
    
    queue_model_change(sender, instance, 'delete')
