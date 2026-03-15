import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from django.conf import settings
from django.core.management import call_command
from django.db import connection
import json

class BackupManager:
    """Handles database backups and recovery"""
    
    def __init__(self):
        self.backup_dir = Path(settings.BASE_DIR) / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self, backup_type='auto'):
        """Create database backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'backup_{backup_type}_{timestamp}'
        
        db_config = settings.DATABASES['default']
        engine = db_config['ENGINE']
        
        if 'sqlite' in engine:
            return self._backup_sqlite(backup_name)
        elif 'postgresql' in engine:
            return self._backup_postgresql(backup_name, db_config)
        elif 'mysql' in engine:
            return self._backup_mysql(backup_name, db_config)
        
        return None
    
    def _backup_sqlite(self, backup_name):
        """Backup SQLite database"""
        db_path = settings.DATABASES['default']['NAME']
        backup_path = self.backup_dir / f'{backup_name}.db'
        
        shutil.copy2(db_path, backup_path)
        
        # Also backup media files
        media_backup = self.backup_dir / f'{backup_name}_media'
        if Path(settings.MEDIA_ROOT).exists():
            shutil.copytree(settings.MEDIA_ROOT, media_backup, dirs_exist_ok=True)
        
        # Create metadata
        self._create_metadata(backup_name, 'sqlite', backup_path)
        
        return backup_path
    
    def _backup_postgresql(self, backup_name, db_config):
        """Backup PostgreSQL database"""
        backup_path = self.backup_dir / f'{backup_name}.sql'
        
        cmd = [
            'pg_dump',
            '-h', db_config.get('HOST', 'localhost'),
            '-p', str(db_config.get('PORT', 5432)),
            '-U', db_config['USER'],
            '-d', db_config['NAME'],
            '-f', str(backup_path)
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        subprocess.run(cmd, env=env, check=True)
        
        self._create_metadata(backup_name, 'postgresql', backup_path)
        
        return backup_path
    
    def _backup_mysql(self, backup_name, db_config):
        """Backup MySQL database"""
        backup_path = self.backup_dir / f'{backup_name}.sql'
        
        cmd = [
            'mysqldump',
            '-h', db_config.get('HOST', 'localhost'),
            '-P', str(db_config.get('PORT', 3306)),
            '-u', db_config['USER'],
            f'-p{db_config["PASSWORD"]}',
            db_config['NAME'],
            '--result-file', str(backup_path)
        ]
        
        subprocess.run(cmd, check=True)
        
        self._create_metadata(backup_name, 'mysql', backup_path)
        
        return backup_path
    
    def _create_metadata(self, backup_name, db_type, backup_path):
        """Create backup metadata file"""
        metadata = {
            'backup_name': backup_name,
            'database_type': db_type,
            'created_at': datetime.now().isoformat(),
            'file_path': str(backup_path),
            'file_size': backup_path.stat().st_size if backup_path.exists() else 0,
            'django_version': settings.VERSION if hasattr(settings, 'VERSION') else 'unknown',
        }
        
        metadata_path = self.backup_dir / f'{backup_name}_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        
        for metadata_file in self.backup_dir.glob('*_metadata.json'):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                backups.append(metadata)
        
        return sorted(backups, key=lambda x: x['created_at'], reverse=True)
    
    def restore_backup(self, backup_name):
        """Restore database from backup"""
        metadata_path = self.backup_dir / f'{backup_name}_metadata.json'
        
        if not metadata_path.exists():
            raise FileNotFoundError(f'Backup {backup_name} not found')
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        db_type = metadata['database_type']
        backup_path = Path(metadata['file_path'])
        
        if db_type == 'sqlite':
            return self._restore_sqlite(backup_path)
        elif db_type == 'postgresql':
            return self._restore_postgresql(backup_path)
        elif db_type == 'mysql':
            return self._restore_mysql(backup_path)
    
    def _restore_sqlite(self, backup_path):
        """Restore SQLite database"""
        db_path = settings.DATABASES['default']['NAME']
        
        # Close all connections
        connection.close()
        
        # Backup current database before restore
        if Path(db_path).exists():
            emergency_backup = Path(db_path).parent / f'{Path(db_path).name}.emergency'
            shutil.copy2(db_path, emergency_backup)
        
        # Restore backup
        shutil.copy2(backup_path, db_path)
        
        return True
    
    def _restore_postgresql(self, backup_path):
        """Restore PostgreSQL database"""
        db_config = settings.DATABASES['default']
        
        cmd = [
            'psql',
            '-h', db_config.get('HOST', 'localhost'),
            '-p', str(db_config.get('PORT', 5432)),
            '-U', db_config['USER'],
            '-d', db_config['NAME'],
            '-f', str(backup_path)
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        subprocess.run(cmd, env=env, check=True)
        
        return True
    
    def _restore_mysql(self, backup_path):
        """Restore MySQL database"""
        db_config = settings.DATABASES['default']
        
        cmd = [
            'mysql',
            '-h', db_config.get('HOST', 'localhost'),
            '-P', str(db_config.get('PORT', 3306)),
            '-u', db_config['USER'],
            f'-p{db_config["PASSWORD"]}',
            db_config['NAME']
        ]
        
        with open(backup_path, 'r') as f:
            subprocess.run(cmd, stdin=f, check=True)
        
        return True
    
    def cleanup_old_backups(self, keep_days=30):
        """Delete backups older than specified days"""
        cutoff_date = datetime.now().timestamp() - (keep_days * 86400)
        
        for metadata_file in self.backup_dir.glob('*_metadata.json'):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            created_at = datetime.fromisoformat(metadata['created_at']).timestamp()
            
            if created_at < cutoff_date:
                # Delete backup file
                backup_path = Path(metadata['file_path'])
                if backup_path.exists():
                    backup_path.unlink()
                
                # Delete media backup if exists
                media_backup = backup_path.parent / f'{backup_path.stem}_media'
                if media_backup.exists():
                    shutil.rmtree(media_backup)
                
                # Delete metadata
                metadata_file.unlink()
    
    def export_database(self, format='json'):
        """Export database in various formats"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_name = f'export_{timestamp}'
        
        if format == 'json':
            export_path = self.backup_dir / f'{export_name}.json'
            call_command('dumpdata', output=str(export_path), indent=2)
        elif format == 'sql':
            export_path = self.create_backup('export')
        
        return export_path
