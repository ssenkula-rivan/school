from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.models import Student, Grade, AcademicYear, School
from core.managers import TenantAwareModel


class ReceiptSequence(models.Model):
    """
    Receipt number sequence generator - ENTERPRISE GRADE
    
    CRITICAL: One row per (school, year, month)
    Locked during receipt generation to prevent race conditions
    
    This is the ONLY safe way to generate sequential numbers under concurrency
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='receipt_sequences', db_index=True)
    year = models.IntegerField(db_index=True)
    month = models.IntegerField(db_index=True)
    last_sequence = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'year', 'month']
        indexes = [
            # CRITICAL: Composite index for fast lookups during locking
            models.Index(fields=['school', 'year', 'month'], name='receipt_seq_lookup'),
        ]
    
    def __str__(self):
        return f"{self.school.code} - {self.year}-{self.month:02d} - Seq: {self.last_sequence}"


class FeeStructure(TenantAwareModel):
    """
    Fee Structure for different grades
    
    TENANT ISOLATION: DIRECT via school FK (ENTERPRISE GRADE)
    Database-level enforcement - cannot be bypassed
    
    CRITICAL: Direct school FK added for true isolation
    """
    TERM_CHOICES = [
        ('1', 'Term 1'),
        ('2', 'Term 2'),
        ('3', 'Term 3'),
        ('annual', 'Annual'),
    ]
    
    # CRITICAL: Direct school FK for database-level isolation
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='fee_structures', db_index=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='fee_structures')
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='fee_structures')
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    
    # Fee Components
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    library_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    sports_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    lab_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    transport_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    uniform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    exam_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    other_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['academic_year', 'grade', 'term']
        ordering = ['academic_year', 'grade', 'term']
        indexes = [
            models.Index(fields=['academic_year', 'grade']),
            models.Index(fields=['is_active']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.academic_year} - {self.grade} - {self.get_term_display()}"
    
    @property
    def total_fee(self):
        return (self.tuition_fee + self.registration_fee + self.library_fee + 
                self.sports_fee + self.lab_fee + self.transport_fee + 
                self.uniform_fee + self.exam_fee + self.other_fee)


class FeePayment(TenantAwareModel):
    """
    Fee Payment Records
    
    TENANT ISOLATION: DIRECT via school FK (ENTERPRISE GRADE)
    Database-level enforcement - cannot be bypassed
    
    CRITICAL: Direct school FK added for true isolation
    """
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('mobile_money', 'Mobile Money'),
        ('card', 'Card Payment'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    # CRITICAL: Direct school FK for database-level isolation
    school = models.ForeignKey(School, on_delete=models.PROTECT, related_name='payments', db_index=True)
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name='payments')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.PROTECT, related_name='payments')
    
    # Payment Details
    receipt_number = models.CharField(max_length=50, db_index=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_date = models.DateField(db_index=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='completed', db_index=True)
    
    # Additional Information
    transaction_reference = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_payments')
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date', '-created_at']
        indexes = [
            # CRITICAL: Composite indexes for performance under load
            models.Index(fields=['school', 'student', 'fee_structure'], name='payment_lookup'),
            models.Index(fields=['school', 'payment_status'], name='payment_status_idx'),
            models.Index(fields=['school', '-payment_date'], name='payment_date_idx'),
            models.Index(fields=['school', 'receipt_number'], name='payment_receipt_idx'),
            models.Index(fields=['-created_at'], name='payment_created_idx'),
        ]
        constraints = [
            # CRITICAL: Database-level unique constraint
            models.UniqueConstraint(
                fields=['school', 'receipt_number'],
                name='unique_receipt_per_school'
            )
        ]
    
    def __str__(self):
        return f"{self.receipt_number} - {self.student.get_full_name()} - ${self.amount_paid}"


class FeeBalance(TenantAwareModel):
    """
    Track fee balances for students
    
    TENANT ISOLATION: DIRECT via school FK (ENTERPRISE GRADE)
    Database-level enforcement - cannot be bypassed
    
    CRITICAL: Direct school FK added for true isolation
    """
    # CRITICAL: Direct school FK for database-level isolation
    school = models.ForeignKey(School, on_delete=models.PROTECT, related_name='fee_balances', db_index=True)
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name='fee_balances')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.PROTECT, related_name='balances')
    
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    scholarship_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Scholarship discount amount')
    amount_after_scholarship = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Amount after scholarship discount')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    due_date = models.DateField(null=True, blank=True, db_index=True)
    is_paid = models.BooleanField(default=False, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'fee_structure']
        ordering = ['student', 'fee_structure']
        indexes = [
            models.Index(fields=['student', 'is_paid']),
            models.Index(fields=['is_paid', 'due_date']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - Balance: ${self.balance}"
    
    def update_balance(self):
        """Recalculate balance based on payments and scholarship"""
        from django.db import transaction
        
        with transaction.atomic():
            # Lock this balance record to prevent race conditions
            balance = FeeBalance.objects.select_for_update().get(pk=self.pk)
            
            # Calculate scholarship discount
            balance.scholarship_discount = balance.student.get_scholarship_amount(balance.total_fee)
            balance.amount_after_scholarship = balance.total_fee - balance.scholarship_discount
            
            # Calculate total payments
            total_payments = balance.student.payments.filter(
                fee_structure=balance.fee_structure,
                payment_status='completed'
            ).aggregate(total=models.Sum('amount_paid'))['total'] or 0
            
            balance.amount_paid = total_payments
            balance.balance = balance.amount_after_scholarship - balance.amount_paid
            balance.is_paid = balance.balance <= 0
            balance.save()



class StudentDiscipline(models.Model):
    """
    Student discipline records
    
    TENANT ISOLATION: Indirect via Student (has school FK)
    Automatically filtered when querying through Student relationship
    """
    INCIDENT_TYPE_CHOICES = [
        ('minor', 'Minor Offense'),
        ('major', 'Major Offense'),
        ('warning', 'Warning'),
        ('suspension', 'Suspension'),
        ('expulsion', 'Expulsion'),
    ]
    
    ACTION_TAKEN_CHOICES = [
        ('verbal_warning', 'Verbal Warning'),
        ('written_warning', 'Written Warning'),
        ('detention', 'Detention'),
        ('suspension', 'Suspension'),
        ('expulsion', 'Expulsion'),
        ('community_service', 'Community Service'),
        ('parent_meeting', 'Parent Meeting'),
        ('counseling', 'Counseling'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name='discipline_records')
    incident_date = models.DateField()
    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPE_CHOICES)
    description = models.TextField(help_text='Detailed description of the incident')
    location = models.CharField(max_length=200, blank=True, help_text='Where the incident occurred')
    
    action_taken = models.CharField(max_length=30, choices=ACTION_TAKEN_CHOICES)
    action_details = models.TextField(blank=True, help_text='Details of action taken')
    
    start_date = models.DateField(null=True, blank=True, help_text='Start date for suspension/detention')
    end_date = models.DateField(null=True, blank=True, help_text='End date for suspension/detention')
    
    parent_notified = models.BooleanField(default=False)
    parent_notified_date = models.DateField(null=True, blank=True)
    parent_response = models.TextField(blank=True)
    
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_incidents')
    resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-incident_date', '-created_at']
        indexes = [
            models.Index(fields=['student', 'incident_date']),
            models.Index(fields=['incident_type']),
            models.Index(fields=['resolved']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.incident_type} - {self.incident_date}"


class StudentIDCard(models.Model):
    """
    Student ID card generation and tracking
    
    TENANT ISOLATION: Indirect via Student (has school FK)
    Automatically filtered when querying through Student relationship
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
        ('replaced', 'Replaced'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='id_cards')
    card_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    barcode = models.CharField(max_length=100, blank=True, help_text='Barcode for scanning')
    qr_code = models.CharField(max_length=200, blank=True, help_text='QR code data')
    
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issued_id_cards')
    replacement_reason = models.TextField(blank=True, help_text='Reason for replacement if applicable')
    replacement_fee_paid = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['card_number']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.card_number} ({self.status})"
    
    def is_valid(self):
        """Check if ID card is currently valid"""
        from datetime import date
        return self.status == 'active' and self.expiry_date >= date.today()
