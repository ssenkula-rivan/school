import json
import requests
from datetime import datetime
from django.db import models, transaction
from django.conf import settings
from django.core.serializers import serialize, deserialize
from pathlib import Path
import hashlib

class SyncManager:
    """Manages offline/online sync for hybrid operation"""
    
    def __init__(self):
        self.sync_dir = Path(settings.BASE_DIR) / 'sync_queue'
        self.sync_dir.mkdir(exist_ok=True)
        self.sync_server = getattr(settings, 'SYNC_SERVER_URL', None)
        
    def is_online(self):
        """
        Check if internet connection is available.
        Uses the configured SYNC_SERVER_URL when available so that
        connectivity is measured against the actual sync endpoint.
        """
        try:
            health_url = None
            if self.sync_server:
                health_url = f"{self.sync_server}/health/" if self.sync_server.endswith('/') is False else f"{self.sync_server}health/"
            else:
                health_url = "https://www.google.com"

            requests.get(health_url, timeout=3)
            return True
        except Exception:
            return False
    
    def queue_change(self, model_name, action, data, record_id=None):
        """Queue a change for sync when online"""
        timestamp = datetime.now().isoformat()
        change_id = hashlib.md5(f"{model_name}{action}{timestamp}".encode()).hexdigest()
        
        change_data = {
            'id': change_id,
            'model': model_name,
            'action': action,  # create, update, delete
            'data': data,
            'record_id': record_id,
            'timestamp': timestamp,
            'synced': False,
            'school_id': getattr(data, 'school_id', None) if hasattr(data, 'school_id') else None
        }
        
        queue_file = self.sync_dir / f'{change_id}.json'
        with open(queue_file, 'w') as f:
            json.dump(change_data, f, indent=2, default=str)
        
        return change_id
    
    def get_pending_changes(self):
        """Get all pending changes to sync"""
        changes = []
        
        for queue_file in self.sync_dir.glob('*.json'):
            with open(queue_file, 'r') as f:
                change = json.load(f)
                if not change.get('synced', False):
                    changes.append(change)
        
        return sorted(changes, key=lambda x: x['timestamp'])
    
    def sync_to_server(self):
        """Sync pending changes to server"""
        if not self.is_online():
            return {'status': 'offline', 'synced': 0}
        
        if not self.sync_server:
            return {'status': 'no_server', 'synced': 0}
        
        pending = self.get_pending_changes()
        synced_count = 0
        errors = []
        
        for change in pending:
            try:
                response = requests.post(
                    f"{self.sync_server}/api/sync/",
                    json=change,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    # Mark as synced
                    change['synced'] = True
                    change['synced_at'] = datetime.now().isoformat()
                    
                    queue_file = self.sync_dir / f"{change['id']}.json"
                    with open(queue_file, 'w') as f:
                        json.dump(change, f, indent=2, default=str)
                    
                    synced_count += 1
                else:
                    errors.append(f"Change {change['id']}: {response.status_code}")
                    
            except Exception as e:
                errors.append(f"Change {change['id']}: {str(e)}")
        
        return {
            'status': 'success',
            'synced': synced_count,
            'pending': len(pending) - synced_count,
            'errors': errors
        }
    
    def sync_from_server(self):
        """Pull changes from server"""
        if not self.is_online():
            return {'status': 'offline', 'pulled': 0}
        
        if not self.sync_server:
            return {'status': 'no_server', 'pulled': 0}
        
        try:
            # Get last sync timestamp
            last_sync = self._get_last_sync_timestamp()
            
            response = requests.get(
                f"{self.sync_server}/api/sync/changes/",
                params={'since': last_sync},
                timeout=10
            )
            
            if response.status_code == 200:
                changes = response.json()
                applied = self._apply_changes(changes)
                
                # Update last sync timestamp
                self._update_last_sync_timestamp()
                
                return {
                    'status': 'success',
                    'pulled': applied
                }
            else:
                return {
                    'status': 'error',
                    'message': f"Server returned {response.status_code}"
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _apply_changes(self, changes):
        """Apply changes from server to local database"""
        applied = 0
        
        for change in changes:
            try:
                with transaction.atomic():
                    model_class = self._get_model_class(change['model'])
                    
                    if change['action'] == 'create':
                        model_class.objects.create(**change['data'])
                        applied += 1
                    elif change['action'] == 'update':
                        obj = model_class.objects.get(id=change['record_id'])
                        for key, value in change['data'].items():
                            setattr(obj, key, value)
                        obj.save()
                        applied += 1
                    elif change['action'] == 'delete':
                        model_class.objects.filter(id=change['record_id']).delete()
                        applied += 1
                        
            except Exception as e:
                print(f"Error applying change: {e}")
                continue
        
        return applied
    
    def _get_model_class(self, model_name):
        """Get model class from string name"""
        from django.apps import apps
        app_label, model = model_name.split('.')
        return apps.get_model(app_label, model)
    
    def _get_last_sync_timestamp(self):
        """Get last sync timestamp"""
        sync_file = self.sync_dir / 'last_sync.txt'
        if sync_file.exists():
            return sync_file.read_text().strip()
        return None
    
    def _update_last_sync_timestamp(self):
        """Update last sync timestamp"""
        sync_file = self.sync_dir / 'last_sync.txt'
        sync_file.write_text(datetime.now().isoformat())
    
    def cleanup_synced(self, days=7):
        """Remove synced changes older than specified days"""
        cutoff = datetime.now().timestamp() - (days * 86400)
        
        for queue_file in self.sync_dir.glob('*.json'):
            with open(queue_file, 'r') as f:
                change = json.load(f)
            
            if change.get('synced', False):
                synced_at = datetime.fromisoformat(change.get('synced_at', change['timestamp']))
                if synced_at.timestamp() < cutoff:
                    queue_file.unlink()
    
    def get_sync_status(self):
        """Get current sync status"""
        pending = self.get_pending_changes()
        online = self.is_online()
        
        return {
            'online': online,
            'pending_changes': len(pending),
            'last_sync': self._get_last_sync_timestamp(),
            'sync_server': self.sync_server or 'Not configured'
        }


class OfflineMiddleware:
    """Middleware to track changes for offline sync"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.sync_manager = SyncManager()
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Auto-sync when we come back online and have pending changes
        try:
            if getattr(settings, "SYNC_ENABLED", True):
                online = self.sync_manager.is_online()
                if online:
                    pending = self.sync_manager.get_pending_changes()
                    if pending:
                        self.sync_manager.sync_to_server()
                        # Optionally pull from server as well
                        self.sync_manager.sync_from_server()
        except Exception:
            # Never let sync errors break user requests
            pass
        
        # Add offline status to response headers
        if hasattr(response, 'headers'):
            response.headers['X-Offline-Mode'] = 'enabled'
            response.headers['X-Online-Status'] = str(self.sync_manager.is_online())
        
        return response
