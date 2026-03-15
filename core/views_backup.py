from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, JsonResponse
from django.views.decorators.http import require_POST
from .backup import BackupManager
from accounts.decorators import role_required

@login_required
@role_required(['admin', 'director'])
def backup_dashboard(request):
    """Backup management dashboard - School admin or director"""
    manager = BackupManager()
    backups = manager.list_backups()
    
    context = {
        'backups': backups,
        'backup_dir': manager.backup_dir,
    }
    
    return render(request, 'core/backup_dashboard.html', context)

@login_required
@role_required(['admin', 'director'])
@require_POST
def create_backup(request):
    """Create new backup - School admin or director"""
    manager = BackupManager()
    
    try:
        backup_path = manager.create_backup('manual')
        messages.success(request, f'Backup created successfully: {backup_path.name}')
    except Exception as e:
        messages.error(request, f'Backup failed: {str(e)}')
    
    return redirect('core:backup_dashboard')

@login_required
@role_required(['admin', 'director'])
def download_backup(request, backup_name):
    """Download backup file - School admin or director"""
    manager = BackupManager()
    backup_path = manager.backup_dir / f'{backup_name}.db'
    
    if not backup_path.exists():
        backup_path = manager.backup_dir / f'{backup_name}.sql'
    
    if backup_path.exists():
        return FileResponse(
            open(backup_path, 'rb'),
            as_attachment=True,
            filename=backup_path.name
        )
    
    messages.error(request, 'Backup file not found')
    return redirect('core:backup_dashboard')

@login_required
@role_required(['admin', 'director'])
def export_database(request):
    """Export database - School admin or director"""
    format_type = request.GET.get('format', 'json')
    
    manager = BackupManager()
    
    try:
        export_path = manager.export_database(format=format_type)
        messages.success(request, f'Database exported: {export_path.name}')
        
        return FileResponse(
            open(export_path, 'rb'),
            as_attachment=True,
            filename=export_path.name
        )
    except Exception as e:
        messages.error(request, f'Export failed: {str(e)}')
        return redirect('core:backup_dashboard')

@login_required
@role_required(['admin', 'director'])
@require_POST
def restore_backup(request, backup_name):
    """Restore from backup - School admin or director"""
    manager = BackupManager()
    
    try:
        manager.restore_backup(backup_name)
        messages.success(request, 'Database restored successfully')
    except Exception as e:
        messages.error(request, f'Restore failed: {str(e)}')
    
    return redirect('core:backup_dashboard')
