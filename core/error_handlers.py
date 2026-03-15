"""
Global Error Handlers - Ensure system never crashes and data is never lost
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
import logging
import traceback

logger = logging.getLogger(__name__)


def handle_404(request, exception):
    """Handle 404 errors gracefully"""
    logger.warning(f"404 Error: {request.path} - User: {request.user}")
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Resource not found',
            'path': request.path
        }, status=404)
    
    return render(request, 'errors/404.html', {
        'path': request.path
    }, status=404)


def handle_500(request):
    """Handle 500 errors gracefully - never show raw errors to users"""
    logger.error(f"500 Error: {request.path} - User: {request.user}")
    logger.error(traceback.format_exc())
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Internal server error',
            'message': 'An error occurred. Please try again or contact support.'
        }, status=500)
    
    return render(request, 'errors/500.html', {
        'support_email': 'support@yourschool.com'
    }, status=500)


def handle_403(request, exception):
    """Handle permission denied errors"""
    logger.warning(f"403 Error: {request.path} - User: {request.user}")
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Permission denied',
            'message': 'You do not have permission to access this resource.'
        }, status=403)
    
    return render(request, 'errors/403.html', status=403)


def handle_400(request, exception):
    """Handle bad request errors"""
    logger.warning(f"400 Error: {request.path} - User: {request.user}")
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Bad request',
            'message': 'Invalid request data.'
        }, status=400)
    
    return render(request, 'errors/400.html', status=400)


class SafeTransactionMixin:
    """
    Mixin to ensure database operations are atomic and safe
    Use this in all views that modify data
    """
    
    @staticmethod
    def safe_save(obj, error_message="Failed to save data"):
        """Safely save an object with error handling"""
        try:
            with transaction.atomic():
                obj.save()
                return True, None
        except Exception as e:
            logger.error(f"{error_message}: {str(e)}")
            logger.error(traceback.format_exc())
            return False, str(e)
    
    @staticmethod
    def safe_delete(obj, error_message="Failed to delete data"):
        """Safely delete an object with error handling"""
        try:
            with transaction.atomic():
                obj.delete()
                return True, None
        except Exception as e:
            logger.error(f"{error_message}: {str(e)}")
            logger.error(traceback.format_exc())
            return False, str(e)
    
    @staticmethod
    def safe_bulk_create(model, objects, error_message="Failed to create records"):
        """Safely bulk create objects"""
        try:
            with transaction.atomic():
                created = model.objects.bulk_create(objects)
                return True, created
        except Exception as e:
            logger.error(f"{error_message}: {str(e)}")
            logger.error(traceback.format_exc())
            return False, str(e)


def safe_view_execution(view_func):
    """
    Decorator to wrap views with error handling
    Ensures views never crash and always return a response
    """
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in view {view_func.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Return appropriate error response
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'An error occurred',
                    'message': 'Please try again or contact support.'
                }, status=500)
            
            return render(request, 'errors/500.html', {
                'error_message': 'An unexpected error occurred. Please try again.',
                'support_email': 'support@yourschool.com'
            }, status=500)
    
    return wrapper


class DataBackupMixin:
    """
    Mixin to create backups before critical operations
    """
    
    @staticmethod
    def backup_before_update(obj, operation_name="update"):
        """Create a backup record before updating"""
        try:
            from django.core import serializers
            backup_data = serializers.serialize('json', [obj])
            
            # Log the backup
            logger.info(f"Backup created for {obj.__class__.__name__} ID {obj.pk} before {operation_name}")
            logger.info(f"Backup data: {backup_data}")
            
            return backup_data
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            return None
