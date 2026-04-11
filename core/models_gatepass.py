"""
Student Gate Pass (Passout) System
Allows head of school/security to issue gate passes for students leaving campus
"""
from django.db import models
from django.contrib.auth.models import User
from .models import School, Student


class GatePass(models.Model):
    """Student gate pass for leaving school premises"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('used', 'Used'),
        ('expired', 'Expired'),
    ]
    
    REASON_CHOICES = [
        ('medical', 'Medical Emergency'),
        ('family', 'Family Emergency'),
        ('appointment', 'Medical Appointment'),
        ('early_dismissal', 'Early Dismissal'),
        ('authorized_leave', 'Authorized Leave'),
        ('parent_request', 'Parent Request'),
        ('school_activity', 'School Activity'),
        ('other', 'Other'),
    ]
    
    # Multi-tenant
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='gate_passes')
    
    # Student Information
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='gate_passes')
    
    # Pass Details
    pass_number = models.CharField(max_length=50, unique=True, db_index=True, help_text='Unique pass number')
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    reason_details = models.TextField(help_text='Detailed reason for leaving')
    
    # Timing
    exit_date = models.DateField(help_text='Date of exit')
    exit_time = models.TimeField(help_text='Expected exit time')
    expected_return_date = models.DateField(null=True, blank=True, help_text='Expected return date')
    expected_return_time = models.TimeField(null=True, blank=True, help_text='Expected return time')
    
    # Actual timing (filled by security)
    actual_exit_time = models.DateTimeField(null=True, blank=True, help_text='Actual exit time')
    actual_return_time = models.DateTimeField(null=True, blank=True, help_text='Actual return time')
    
    # Authorization
    requested_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='requested_passes',
        help_text='Person who requested the pass (teacher, parent, etc.)'
    )
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_passes',
        help_text='Head of school or authorized person'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Security tracking
    exit_security = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exit_passes_processed',
        help_text='Security who processed exit'
    )
    return_security = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='return_passes_processed',
        help_text='Security who processed return'
    )
    
    # Parent/Guardian Information
    parent_name = models.CharField(max_length=200, help_text='Parent/Guardian name')
    parent_phone = models.CharField(max_length=20, help_text='Parent/Guardian phone')
    parent_id_number = models.CharField(max_length=50, blank=True, help_text='Parent ID/Passport number')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    rejection_reason = models.TextField(blank=True, help_text='Reason for rejection')
    
    # Notes
    notes = models.TextField(blank=True, help_text='Additional notes')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['school', 'status']),
            models.Index(fields=['student', '-created_at']),
            models.Index(fields=['pass_number']),
            models.Index(fields=['exit_date']),
        ]
    
    def __str__(self):
        return f"Pass #{self.pass_number} - {self.student.get_full_name()} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Generate pass number if not set
        if not self.pass_number:
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            count = GatePass.objects.filter(
                school=self.school,
                created_at__date=timezone.now().date()
            ).count() + 1
            self.pass_number = f"GP-{self.school.code}-{date_str}-{count:04d}"
        
        super().save(*args, **kwargs)
    
    def approve(self, approved_by_user):
        """Approve the gate pass"""
        from django.utils import timezone
        self.status = 'approved'
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        self.save()
    
    def reject(self, rejected_by_user, reason):
        """Reject the gate pass"""
        self.status = 'rejected'
        self.approved_by = rejected_by_user
        self.rejection_reason = reason
        self.save()
    
    def mark_exit(self, security_user):
        """Mark student as exited"""
        from django.utils import timezone
        self.actual_exit_time = timezone.now()
        self.exit_security = security_user
        self.status = 'used'
        self.save()
    
    def mark_return(self, security_user):
        """Mark student as returned"""
        from django.utils import timezone
        self.actual_return_time = timezone.now()
        self.return_security = security_user
        self.save()


class Expense(models.Model):
    """School expense tracking"""
    
    EXPENSE_TYPE_CHOICES = [
        ('operational', 'Operational Expense'),
        ('capital', 'Capital Expenditure'),
        ('salary', 'Salary & Wages'),
        ('utilities', 'Utilities'),
        ('maintenance', 'Maintenance & Repairs'),
        ('supplies', 'Supplies & Materials'),
        ('transport', 'Transportation'),
        ('food', 'Food & Catering'),
        ('events', 'Events & Activities'),
        ('other', 'Other'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('cheque', 'Cheque'),
        ('card', 'Card Payment'),
    ]
    
    # Multi-tenant
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='expenses')
    
    # Expense Details
    expense_number = models.CharField(max_length=50, unique=True, db_index=True)
    expense_type = models.CharField(max_length=50, choices=EXPENSE_TYPE_CHOICES)
    category = models.CharField(max_length=100, help_text='Specific category (e.g., Electricity, Stationery)')
    description = models.TextField()
    
    # Financial
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='UGX')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    # Vendor/Payee
    vendor_name = models.CharField(max_length=200)
    vendor_phone = models.CharField(max_length=20, blank=True)
    vendor_email = models.EmailField(blank=True)
    vendor_tin = models.CharField(max_length=50, blank=True, help_text='Tax Identification Number')
    
    # Documentation
    receipt_image = models.ImageField(upload_to='expenses/receipts/', blank=True, null=True)
    invoice_image = models.ImageField(upload_to='expenses/invoices/', blank=True, null=True)
    supporting_documents = models.FileField(upload_to='expenses/documents/', blank=True, null=True)
    
    # Dates
    expense_date = models.DateField(help_text='Date expense was incurred')
    payment_date = models.DateField(help_text='Date payment was made')
    
    # Approval
    requested_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='requested_expenses',
        help_text='Person who requested the expense'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_expenses',
        help_text='Person who approved the expense (Admin/Director)'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Payment Processing
    paid_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paid_expenses',
        help_text='Bursar/Accountant who processed the payment'
    )
    paid_at = models.DateTimeField(null=True, blank=True, help_text='When payment was processed')
    
    # Bank/Account Information
    payment_reference = models.CharField(max_length=100, blank=True, help_text='Transaction reference number')
    bank_account = models.CharField(max_length=100, blank=True, help_text='Bank account used for payment')
    
    # Status
    is_approved = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False, help_text='Payment completed')
    is_verified = models.BooleanField(default=False, help_text='Payment verified by accountant')
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-expense_date', '-created_at']
        indexes = [
            models.Index(fields=['school', 'expense_date']),
            models.Index(fields=['expense_type']),
            models.Index(fields=['is_approved', 'is_paid']),
        ]
    
    def __str__(self):
        return f"{self.expense_number} - {self.vendor_name} - UGX {self.amount:,.0f}"
    
    def save(self, *args, **kwargs):
        # Generate expense number if not set
        if not self.expense_number:
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m')
            count = Expense.objects.filter(
                school=self.school,
                created_at__year=timezone.now().year,
                created_at__month=timezone.now().month
            ).count() + 1
            self.expense_number = f"EXP-{self.school.code}-{date_str}-{count:04d}"
        
        super().save(*args, **kwargs)
    
    def approve(self, approved_by_user):
        """Approve the expense"""
        from django.utils import timezone
        self.is_approved = True
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        self.save()
    
    def mark_as_paid(self, paid_by_user, payment_reference='', bank_account=''):
        """Mark expense as paid by bursar/accountant"""
        from django.utils import timezone
        self.is_paid = True
        self.paid_by = paid_by_user
        self.paid_at = timezone.now()
        self.payment_reference = payment_reference
        self.bank_account = bank_account
        self.save()
    
    def verify_payment(self):
        """Verify payment (usually by accountant)"""
        self.is_verified = True
        self.save()
    
    def get_status_display_text(self):
        """Get human-readable status"""
        if not self.is_approved:
            return 'Pending Approval'
        elif not self.is_paid:
            return 'Approved - Awaiting Payment'
        elif not self.is_verified:
            return 'Paid - Awaiting Verification'
        else:
            return 'Completed'
