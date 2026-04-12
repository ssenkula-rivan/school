from django.urls import path
from . import views, views_backup, views_sync, views_departments, views_setup

app_name = 'core'

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='health_check'),
    
    # School Setup
    path('setup/', views_setup.setup_school_data, name='setup_school_data'),
    
    # Department Management
    path('departments/', views_departments.department_list, name='department_list'),
    path('departments/create/', views_departments.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views_departments.department_edit, name='department_edit'),
    
    # Backup URLs
    path('backup/', views_backup.backup_dashboard, name='backup_dashboard'),
    path('backup/create/', views_backup.create_backup, name='create_backup'),
    path('backup/download/<str:backup_name>/', views_backup.download_backup, name='download_backup'),
    path('backup/export/', views_backup.export_database, name='export_database'),
    path('backup/restore/<str:backup_name>/', views_backup.restore_backup, name='restore_backup'),
    
    # Sync URLs
    path('sync/', views_sync.sync_dashboard, name='sync_dashboard'),
    path('sync/now/', views_sync.sync_now, name='sync_now'),
    path('sync/status/', views_sync.sync_status_api, name='sync_status_api'),
    path('sync/cleanup/', views_sync.cleanup_synced, name='cleanup_synced'),
]
