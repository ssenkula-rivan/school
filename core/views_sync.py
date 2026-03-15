from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .sync_manager import SyncManager
from accounts.decorators import role_required

@login_required
@role_required(['admin', 'director'])
def sync_dashboard(request):
    """Sync management dashboard"""
    manager = SyncManager()
    status = manager.get_sync_status()
    pending = manager.get_pending_changes()
    
    context = {
        'status': status,
        'pending_changes': pending[:50],  # Show last 50
        'total_pending': len(pending),
    }
    
    return render(request, 'core/sync_dashboard.html', context)

@login_required
@role_required(['admin', 'director'])
@require_POST
def sync_now(request):
    """Trigger manual sync"""
    manager = SyncManager()
    
    if not manager.is_online():
        messages.warning(request, 'System is offline. Changes will sync automatically when online.')
        return redirect('core:sync_dashboard')
    
    # Push changes
    push_result = manager.sync_to_server()
    
    # Pull changes
    pull_result = manager.sync_from_server()
    
    if push_result['status'] == 'success':
        messages.success(request, f"Synced {push_result['synced']} changes to server")
    
    if pull_result['status'] == 'success':
        messages.success(request, f"Pulled {pull_result['pulled']} changes from server")
    
    if push_result.get('errors'):
        for error in push_result['errors']:
            messages.error(request, error)
    
    return redirect('core:sync_dashboard')

@login_required
def sync_status_api(request):
    """API endpoint for sync status"""
    manager = SyncManager()
    status = manager.get_sync_status()
    
    return JsonResponse(status)

@login_required
@role_required(['admin', 'director'])
@require_POST
def cleanup_synced(request):
    """Cleanup old synced changes"""
    manager = SyncManager()
    manager.cleanup_synced(days=7)
    
    messages.success(request, 'Cleaned up old synced changes')
    return redirect('core:sync_dashboard')
