"""
Custom managers for multi-tenant support - ENTERPRISE GRADE
"""
from django.db import models
from django.core.exceptions import ImproperlyConfigured


class TenantIsolationError(Exception):
    """Raised when tenant isolation is violated"""
    pass


class TenantManager(models.Manager):
    """
    Automatically filter by school for multi-tenant isolation
    
    CRITICAL SECURITY - FAIL HARD APPROACH:
    - NEVER returns unfiltered data if no school context
    - Returns .none() to prevent data leakage
    - Forces explicit handling via _unfiltered manager
    - Prevents accidental cross-tenant queries
    
    SAFE USAGE:
        Student.objects.all()  # Auto-filtered by current school
        Student.objects.filter(status='active')  # Auto-filtered
    
    EXPLICIT UNFILTERED (DANGEROUS):
        Student._unfiltered.all()  # Requires conscious decision
    """
    
    def get_queryset(self):
        from .middleware import get_current_school
        
        queryset = super().get_queryset()
        
        # Check if model has school field
        if not hasattr(self.model, 'school'):
            # Model doesn't have school field - return normal queryset
            return queryset
        
        # Get current school from context
        school = get_current_school()
        
        # CRITICAL: FAIL HARD if no school context
        # This is the SAFEST approach for multi-tenant SaaS
        if school is None:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"TenantManager: No school context for {self.model.__name__}.objects query. "
                f"Returning empty queryset. Use {self.model.__name__}._unfiltered if you need all schools."
            )
            # Return empty queryset - NEVER return all data
            # This prevents accidental data leakage
            return queryset.none()
        
        # Filter by school
        return queryset.filter(school=school)
    
    def for_school(self, school):
        """
        Explicitly query for a specific school
        
        Usage:
            Student.objects.for_school(school).filter(status='active')
        """
        if school is None:
            raise TenantIsolationError(
                "Cannot query with school=None. "
                "Use _unfiltered manager if you need all schools."
            )
        return super().get_queryset().filter(school=school)
    
    def all_schools(self):
        """
        DEPRECATED: Use _unfiltered manager instead
        
        This method exists for backward compatibility but will be removed.
        Raises error to force migration to _unfiltered.
        """
        raise TenantIsolationError(
            "all_schools() is deprecated and disabled for security. "
            "Use Model._unfiltered.all() instead to make your intent explicit."
        )


class TenantAwareModel(models.Model):
    """
    Base model for tenant-aware models
    
    SECURITY FEATURES:
    - objects: Automatically filtered by school (SAFE)
    - _unfiltered: Explicit unfiltered access (DANGEROUS - use with caution)
    
    Usage:
        class MyModel(TenantAwareModel):
            school = models.ForeignKey(School, on_delete=models.CASCADE)
            name = models.CharField(...)
        
        # Safe - automatically filtered
        MyModel.objects.all()
        
        # Explicit - requires conscious decision
        MyModel._unfiltered.all()  # Only for admin/superuser
    """
    
    class Meta:
        abstract = True
    
    # Default manager - SAFE (auto-filtered)
    objects = TenantManager()
    
    # Unfiltered manager - DANGEROUS (explicit name warns developers)
    _unfiltered = models.Manager()
    
    def save(self, *args, **kwargs):
        """
        Override save to enforce school assignment
        
        CRITICAL SECURITY:
        - NEVER auto-sets school (explicit > magic)
        - FAILS HARD if school not set on new records
        - Prevents background jobs from creating untenanted data
        - Forces developers to explicitly assign school
        
        WHY NO AUTO-INJECT:
        - Background jobs have no request context
        - Auto-inject would silently create None school records
        - Explicit assignment prevents data corruption
        """
        if hasattr(self, 'school_id'):
            # Model has school field
            if self.school_id is None and self.pk is None:
                # New record without school - FAIL HARD
                raise TenantIsolationError(
                    f"{self.__class__.__name__} requires explicit school assignment. "
                    f"Set instance.school before saving. "
                    f"Never rely on auto-injection - it's dangerous in background jobs."
                )
        
        super().save(*args, **kwargs)
