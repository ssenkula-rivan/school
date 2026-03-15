"""
Audit logging for critical operations - ENTERPRISE GRADE
"""
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Centralized audit logging for critical operations
    
    CRITICAL: All audit logs are created INSIDE the same transaction
    as the operation they're logging. This ensures:
    - If operation fails, audit log is rolled back
    - If audit log fails, operation is rolled back
    - No orphaned audit entries
    """
    
    @staticmethod
    def log_payment(user, payment, action='create', description='', ip_address=None, user_agent=''):
        """
        Log payment operations
        
        MUST be called inside the same transaction as the payment operation
        """
        from accounts.models import AuditLog
        
        try:
            AuditLog.objects.create(
                user=user,
                action=action,
                content_type=ContentType.objects.get_for_model(payment),
                object_id=payment.id,
                description=description or f"Payment {action}: {payment.receipt_number} - ${payment.amount_paid}",
                ip_address=ip_address,
                user_agent=user_agent or ''
            )
        except Exception as e:
            logger.error(
                f"Failed to create audit log for payment {payment.id}: {e}",
                exc_info=True
            )
            # Re-raise to rollback transaction
            raise
    
    @staticmethod
    def log_student_change(user, student, action, description='', ip_address=None, user_agent=''):
        """
        Log student record changes
        
        MUST be called inside the same transaction as the student operation
        """
        from accounts.models import AuditLog
        
        try:
            AuditLog.objects.create(
                user=user,
                action=action,
                content_type=ContentType.objects.get_for_model(student),
                object_id=student.id,
                description=description or f"Student {action}: {student.get_full_name()}",
                ip_address=ip_address,
                user_agent=user_agent or ''
            )
        except Exception as e:
            logger.error(
                f"Failed to create audit log for student {student.id}: {e}",
                exc_info=True
            )
            raise
    
    @staticmethod
    def log_grade_change(user, mark, old_value, new_value, ip_address=None, user_agent=''):
        """
        Log grade changes
        
        MUST be called inside the same transaction as the grade update
        """
        from accounts.models import AuditLog
        
        try:
            AuditLog.objects.create(
                user=user,
                action='update',
                content_type=ContentType.objects.get_for_model(mark),
                object_id=mark.id,
                description=f"Grade changed for {mark.student.get_full_name()} in {mark.subject.name}: {old_value} → {new_value}",
                ip_address=ip_address,
                user_agent=user_agent or ''
            )
        except Exception as e:
            logger.error(
                f"Failed to create audit log for mark {mark.id}: {e}",
                exc_info=True
            )
            raise
    
    @staticmethod
    def log_permission_change(user, target_user, old_role, new_role, ip_address=None, user_agent=''):
        """
        Log permission/role changes
        
        MUST be called inside the same transaction as the role update
        """
        from accounts.models import AuditLog
        
        try:
            AuditLog.objects.create(
                user=user,
                action='update',
                content_type=ContentType.objects.get_for_model(target_user),
                object_id=target_user.id,
                description=f"Role changed for {target_user.get_full_name()}: {old_role} → {new_role}",
                ip_address=ip_address,
                user_agent=user_agent or ''
            )
        except Exception as e:
            logger.error(
                f"Failed to create audit log for user {target_user.id}: {e}",
                exc_info=True
            )
            raise
    
    @staticmethod
    def log_data_export(user, model_name, record_count, filters='', ip_address=None, user_agent=''):
        """
        Log data exports
        
        NOTE: Export logs are NOT transactional (export doesn't modify data)
        """
        from accounts.models import AuditLog
        
        try:
            AuditLog.objects.create(
                user=user,
                action='export',
                description=f"Exported {record_count} {model_name} records. Filters: {filters}",
                ip_address=ip_address,
                user_agent=user_agent or ''
            )
        except Exception as e:
            # Don't fail export if audit log fails
            logger.error(
                f"Failed to create audit log for export: {e}",
                exc_info=True
            )
    
    @staticmethod
    def log_bulk_operation(user, model_name, operation, count, description='', ip_address=None, user_agent=''):
        """
        Log bulk operations
        
        MUST be called inside the same transaction as the bulk operation
        """
        from accounts.models import AuditLog
        
        try:
            AuditLog.objects.create(
                user=user,
                action=operation,
                description=description or f"Bulk {operation} on {count} {model_name} records",
                ip_address=ip_address,
                user_agent=user_agent or ''
            )
        except Exception as e:
            logger.error(
                f"Failed to create audit log for bulk operation: {e}",
                exc_info=True
            )
            raise
    
    @staticmethod
    def get_client_ip(request):
        """
        Get client IP address from request
        
        Handles proxy headers correctly
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_user_agent(request):
        """Get user agent from request"""
        return request.META.get('HTTP_USER_AGENT', '')[:500]  # Truncate to 500 chars
