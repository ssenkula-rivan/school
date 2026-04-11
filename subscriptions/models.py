"""
Subscription and Plan models for SaaS platform - ENTERPRISE GRADE
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


class PlanLimitExceeded(Exception):
    """Raised when school exceeds plan limits"""
    pass


class FeatureNotAllowed(Exception):
    """Raised when feature not available in plan"""
    pass


class Plan(models.Model):
    """
    Subscription plans for schools
    
    CRITICAL: Defines limits and features per plan
    """
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('lifetime', 'Lifetime'),
    ]
    
    # Basic Info
    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    billing_cycle = models.CharField(
        max_length=20, 
        choices=BILLING_CYCLE_CHOICES,
        default='monthly'
    )
    
    # Limits
    max_students = models.IntegerField(
        default=100,
        validators=[MinValueValidator(1)],
        help_text='Maximum number of active students'
    )
    max_teachers = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1)],
        help_text='Maximum number of teachers'
    )
    max_staff = models.IntegerField(
        default=20,
        validators=[MinValueValidator(1)],
        help_text='Maximum number of total staff'
    )
    max_storage_gb = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1)],
        help_text='Maximum storage in GB'
    )
    
    # Features (JSON field for flexibility)
    feature_flags = models.JSONField(
        default=dict,
        help_text='Feature flags: {"advanced_reports": true, "sms_integration": false, ...}'
    )
    
    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    is_public = models.BooleanField(
        default=True,
        help_text='Show on pricing page'
    )
    sort_order = models.IntegerField(default=0)
    
    # Trial
    trial_days = models.IntegerField(
        default=14,
        validators=[MinValueValidator(0)],
        help_text='Number of trial days (0 = no trial)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'price']
        indexes = [
            models.Index(fields=['is_active', 'is_public']),
        ]
    
    def __str__(self):
        return f"{self.name} - ${self.price}/{self.billing_cycle}"
    
    def get_feature(self, feature_name, default=False):
        """Get feature flag value"""
        return self.feature_flags.get(feature_name, default)


class Subscription(models.Model):
    """
    School subscription - CRITICAL for SaaS revenue
    
    SECURITY:
    - Checked in middleware (blocks access if expired/suspended)
    - Checked before creating students/staff (enforces limits)
    - Linked to payment gateway for verification
    """
    STATUS_CHOICES = [
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Relationships
    school = models.OneToOneField(
        'core.School',
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='trial',
        db_index=True
    )
    
    # Billing Period
    current_period_start = models.DateField(db_index=True)
    current_period_end = models.DateField(db_index=True)
    
    # Trial
    trial_start = models.DateField(null=True, blank=True)
    trial_end = models.DateField(null=True, blank=True, db_index=True)
    
    # Payment Gateway Integration
    external_payment_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        help_text='Stripe/Flutterwave/Paystack subscription ID'
    )
    external_customer_id = models.CharField(
        max_length=255,
        blank=True,
        help_text='External customer ID'
    )
    
    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.TextField(blank=True)
    cancel_at_period_end = models.BooleanField(
        default=False,
        help_text='Cancel when current period ends'
    )
    
    # System
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'current_period_end']),
            models.Index(fields=['trial_end']),
            models.Index(fields=['external_payment_id']),
        ]
    
    def __str__(self):
        return f"{self.school.code} - {self.plan.name} ({self.status})"
    
    @property
    def is_active(self):
        """Check if subscription is currently active"""
        today = date.today()
        
        if self.status == 'active':
            return self.current_period_end >= today
        
        if self.status == 'trial':
            return self.trial_end and self.trial_end >= today
        
        return False
    
    @property
    def is_trial(self):
        """Check if in trial period"""
        if self.status != 'trial':
            return False
        
        if not self.trial_end:
            return False
        
        return self.trial_end >= date.today()
    
    @property
    def days_until_expiry(self):
        """Days until subscription expires"""
        if self.status == 'trial' and self.trial_end:
            return (self.trial_end - date.today()).days
        
        if self.status == 'active':
            return (self.current_period_end - date.today()).days
        
        return 0
    
    def check_student_limit(self):
        """
        Check if school can add more students
        
        Raises PlanLimitExceeded if limit reached
        """
        from core.models import Student
        
        current_count = Student.objects.filter(
            school=self.school,
            status='active'
        ).count()
        
        if current_count >= self.plan.max_students:
            raise PlanLimitExceeded(
                f"School has reached maximum student limit ({self.plan.max_students}). "
                f"Current: {current_count}. Please upgrade your plan."
            )
    
    def check_staff_limit(self):
        """
        Check if school can add more staff
        
        Raises PlanLimitExceeded if limit reached
        """
        from accounts.models import UserProfile
        
        current_count = UserProfile.objects.filter(
            school=self.school,
            user__is_active=True
        ).exclude(role='student').count()
        
        if current_count >= self.plan.max_staff:
            raise PlanLimitExceeded(
                f"School has reached maximum staff limit ({self.plan.max_staff}). "
                f"Current: {current_count}. Please upgrade your plan."
            )
    
    def has_feature(self, feature_name):
        """Check if plan has specific feature"""
        return self.plan.get_feature(feature_name, default=False)
    
    def renew(self):
        """Renew subscription for next period"""
        if self.plan.billing_cycle == 'monthly':
            delta = timedelta(days=30)
        elif self.plan.billing_cycle == 'yearly':
            delta = timedelta(days=365)
        else:
            raise ValueError(f"Cannot renew {self.plan.billing_cycle} subscription")
        
        self.current_period_start = self.current_period_end + timedelta(days=1)
        self.current_period_end = self.current_period_start + delta
        self.status = 'active'
        self.save()
        
        logger.info(
            f"Subscription renewed: {self.school.code}",
            extra={
                'school_id': self.school.id,
                'plan': self.plan.name,
                'period_end': self.current_period_end
            }
        )
    
    def suspend(self, reason=''):
        """Suspend subscription"""
        self.status = 'suspended'
        self.cancel_reason = reason
        self.save()
        
        logger.warning(
            f"Subscription suspended: {self.school.code}",
            extra={
                'school_id': self.school.id,
                'reason': reason
            }
        )
    
    def cancel(self, reason='', immediate=False):
        """Cancel subscription"""
        self.cancelled_at = timezone.now()
        self.cancel_reason = reason
        
        if immediate:
            self.status = 'cancelled'
            self.current_period_end = date.today()
        else:
            self.cancel_at_period_end = True
        
        self.save()
        
        logger.info(
            f"Subscription cancelled: {self.school.code} (immediate={immediate})",
            extra={
                'school_id': self.school.id,
                'reason': reason
            }
        )


class SubscriptionInvoice(models.Model):
    """
    Invoice records for subscription payments
    
    CRITICAL: Audit trail for all payments
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    
    # Invoice Details
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(max_length=3, default='UGX')
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    
    # Dates
    issue_date = models.DateField(db_index=True)
    due_date = models.DateField(db_index=True)
    paid_date = models.DateField(null=True, blank=True)
    
    # Payment Gateway
    external_invoice_id = models.CharField(max_length=255, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=255, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['subscription', 'status']),
            models.Index(fields=['-issue_date']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.subscription.school.code} - ${self.amount}"
    
    def mark_paid(self, payment_method='', transaction_id=''):
        """Mark invoice as paid"""
        self.status = 'paid'
        self.paid_date = date.today()
        self.payment_method = payment_method
        self.transaction_id = transaction_id
        self.save()
        
        logger.info(
            f"Invoice paid: {self.invoice_number}",
            extra={
                'invoice_id': self.id,
                'amount': self.amount,
                'school_id': self.subscription.school.id
            }
        )
