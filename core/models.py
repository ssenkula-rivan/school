from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.cache import cache
from decimal import Decimal
from .managers import TenantAwareModel


class School(models.Model):
    """Multi-tenant school model - CRITICAL for SaaS"""
    SCHOOL_TYPE_CHOICES = [
        ('nursery', 'Nursery'),
        ('primary', 'Primary School'),
        ('secondary', 'Secondary School'),
        ('college', 'College'),
        ('university', 'University'),
        ('combined', 'Combined'),
    ]
    
    INSTITUTION_TYPE_CHOICES = [
        ('government', 'Government'),
        ('private', 'Private'),
        ('religious', 'Religious'),
        ('international', 'International'),
        ('vocational', 'Vocational'),
        ('special_needs', 'Special Needs'),
        ('boarding', 'Boarding'),
        ('day', 'Day School'),
        ('mixed', 'Mixed'),
    ]
    
    # Basic Info
    name = models.CharField(max_length=200, unique=True, db_index=True)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    school_type = models.CharField(max_length=20, choices=SCHOOL_TYPE_CHOICES, db_index=True)
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_TYPE_CHOICES)
    
    # Contact
    email = models.EmailField()
    email_domain = models.CharField(max_length=100, unique=True, db_index=True, help_text="Email domain for school users (e.g., kawandass.edu)")
    phone = models.CharField(max_length=20)
    address = models.TextField()
    website = models.URLField(blank=True)
    
    # Subscription (for SaaS)
    is_active = models.BooleanField(default=True, db_index=True)
    subscription_start = models.DateField()
    subscription_end = models.DateField()
    max_students = models.IntegerField(default=1000)
    max_staff = models.IntegerField(default=100)
    
    # Settings
    currency = models.CharField(max_length=3, default='USD')
    timezone = models.CharField(max_length=50, default='UTC')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def save(self, *args, **kwargs):
        """
        Override save to invalidate cache on school updates
        
        CRITICAL SECURITY: Cache invalidation prevents stale security data
        """
        super().save(*args, **kwargs)
        
        # Invalidate all caches for this school
        cache.delete(f'school_subdomain:{self.code}')
        cache.delete(f'school_id:{self.id}')
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"School cache invalidated: {self.code}",
            extra={'school_id': self.id, 'is_active': self.is_active}
        )


class Department(TenantAwareModel):
    """Single Department model for entire system - TENANT AWARE"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['school', 'name']
        ordering = ['school', 'name']
        indexes = [
            models.Index(fields=['school', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.school.code} - {self.name}"


class AcademicYear(TenantAwareModel):
    """Academic Year per school - TENANT AWARE"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='academic_years')
    name = models.CharField(max_length=50, db_index=True)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    is_current = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['school', 'name']
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['school', 'is_current']),
            models.Index(fields=['school', '-start_date']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['school'],
                condition=models.Q(is_current=True),
                name='unique_current_year_per_school'
            )
        ]
    
    def __str__(self):
        return f"{self.school.code} - {self.name}"
    
    def save(self, *args, **kwargs):
        from django.db import transaction
        
        if self.is_current:
            with transaction.atomic():
                # Use _unfiltered to update across school boundary
                AcademicYear._unfiltered.select_for_update().filter(
                    school=self.school,
                    is_current=True
                ).exclude(id=self.id).update(is_current=False)
                super(TenantAwareModel, self).save(*args, **kwargs)
        else:
            super(TenantAwareModel, self).save(*args, **kwargs)


class Grade(TenantAwareModel):
    """Grade/Class Level per school - TENANT AWARE"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='grades')
    name = models.CharField(max_length=50, db_index=True)
    level = models.IntegerField(db_index=True)
    description = models.TextField(blank=True)
    capacity = models.IntegerField(default=40)
    
    class Meta:
        unique_together = ['school', 'name']
        ordering = ['school', 'level']
        indexes = [
            models.Index(fields=['school', 'level']),
        ]
    
    def __str__(self):
        return f"{self.school.code} - {self.name}"


class Student(TenantAwareModel):
    """Student model - moved from fees app - TENANT AWARE"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('graduated', 'Graduated'),
        ('transferred', 'Transferred'),
        ('suspended', 'Suspended'),
        ('expelled', 'Expelled'),
    ]
    
    SCHOLARSHIP_STATUS_CHOICES = [
        ('none', 'No Scholarship'),
        ('partial', 'Partial Scholarship'),
        ('full', 'Full Scholarship'),
    ]
    
    # Multi-tenant
    school = models.ForeignKey(School, on_delete=models.PROTECT, related_name='students', db_index=True)
    
    # Basic Information
    admission_number = models.CharField(max_length=20, db_index=True)
    first_name = models.CharField(max_length=100, db_index=True)
    last_name = models.CharField(max_length=100, db_index=True)
    middle_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(db_index=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Academic Information
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, related_name='students', db_index=True)
    admission_date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index=True)
    
    # Scholarship Information
    scholarship_status = models.CharField(max_length=20, choices=SCHOLARSHIP_STATUS_CHOICES, default='none', db_index=True)
    scholarship_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    scholarship_remarks = models.TextField(blank=True)
    
    # Contact Information
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField()
    
    # Guardian Information
    guardian_name = models.CharField(max_length=200)
    guardian_relationship = models.CharField(max_length=50)
    guardian_phone = models.CharField(max_length=15, db_index=True)
    guardian_email = models.EmailField(blank=True)
    guardian_address = models.TextField(blank=True)
    
    # Medical Information
    blood_group = models.CharField(max_length=5, blank=True)
    allergies = models.TextField(blank=True)
    medical_conditions = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    
    # Document Uploads
    birth_certificate = models.FileField(upload_to='student_documents/birth_certificates/', blank=True, null=True)
    previous_report_card = models.FileField(upload_to='student_documents/report_cards/', blank=True, null=True)
    transfer_certificate = models.FileField(upload_to='student_documents/transfers/', blank=True, null=True)
    other_documents = models.FileField(upload_to='student_documents/others/', blank=True, null=True)
    
    # System fields
    photo = models.ImageField(upload_to='students/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'admission_number']
        ordering = ['school', 'admission_number']
        indexes = [
            models.Index(fields=['school', 'status']),
            models.Index(fields=['school', 'grade', 'status']),
            models.Index(fields=['school', 'first_name', 'last_name']),
            models.Index(fields=['school', 'scholarship_status']),
        ]
    
    def __str__(self):
        return f"{self.school.code} - {self.admission_number} - {self.get_full_name()}"
    
    def get_full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    @property
    def has_scholarship(self):
        return self.scholarship_status != 'none' and self.scholarship_percentage > 0
    
    def calculate_fee_with_scholarship(self, original_fee):
        if not self.has_scholarship:
            return original_fee
        discount = original_fee * (self.scholarship_percentage / 100)
        return original_fee - discount
    
    def get_scholarship_amount(self, original_fee):
        if not self.has_scholarship:
            return Decimal('0.00')
        return original_fee * (self.scholarship_percentage / 100)
    
    def save(self, *args, **kwargs):
        """
        Override save to enforce plan limits
        
        CRITICAL: Prevents exceeding subscription limits
        """
        # Check if new student (not update)
        if not self.pk and self.status == 'active':
            # Check subscription limit
            if hasattr(self.school, 'subscription'):
                try:
                    self.school.subscription.check_student_limit()
                except Exception as e:
                    # Import here to avoid circular import
                    from subscriptions.models import PlanLimitExceeded
                    if isinstance(e, PlanLimitExceeded):
                        raise
        
        super().save(*args, **kwargs)
