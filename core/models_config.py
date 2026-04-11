"""
School Configuration System - NOTHING HARDCODED
All school-specific settings are stored here and configurable
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import School
from core.managers import TenantAwareModel
import json


class SchoolSettings(TenantAwareModel):
    """
    Master configuration for each school
    Stores ALL configurable settings - NOTHING hardcoded
    """
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='settings')
    
    # Academic Settings
    academic_year_format = models.CharField(max_length=50, default='YYYY-YYYY', help_text='e.g., 2024-2025, 2024, AY2024')
    term_naming = models.CharField(max_length=20, default='term', help_text='term, semester, quarter, trimester')
    uses_streams = models.BooleanField(default=True, help_text='Does school use streams/sections?')
    stream_naming = models.CharField(max_length=20, default='stream', help_text='stream, section, class, division')
    
    # Grading Settings
    grading_system = models.CharField(max_length=20, default='percentage', help_text='percentage, gpa, letter, custom')
    pass_mark = models.DecimalField(max_digits=5, decimal_places=2, default=50.00, help_text='Minimum passing grade')
    max_mark = models.DecimalField(max_digits=5, decimal_places=2, default=100.00, help_text='Maximum possible grade')
    
    # Financial Settings
    currency_code = models.CharField(max_length=3, default='UGX', help_text='ISO currency code')
    currency_symbol = models.CharField(max_length=10, default='UGX')
    tax_enabled = models.BooleanField(default=False)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(0), MaxValueValidator(100)])
    tax_name = models.CharField(max_length=50, default='VAT', help_text='VAT, GST, Sales Tax, etc.')
    
    # Numbering Formats
    invoice_prefix = models.CharField(max_length=10, default='INV', help_text='Invoice number prefix')
    invoice_format = models.CharField(max_length=50, default='{prefix}-{year}-{number:05d}', help_text='Use {prefix}, {year}, {number}')
    receipt_prefix = models.CharField(max_length=10, default='RCP')
    receipt_format = models.CharField(max_length=50, default='{prefix}-{year}-{number:05d}')
    admission_number_format = models.CharField(max_length=50, default='{year}/{number:04d}')
    
    # Attendance Settings
    attendance_required = models.BooleanField(default=True)
    minimum_attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=75.00)
    late_arrival_minutes = models.IntegerField(default=15, help_text='Minutes after which student is marked late')
    
    # Promotion Rules
    auto_promotion = models.BooleanField(default=False)
    promotion_pass_mark = models.DecimalField(max_digits=5, decimal_places=2, default=50.00)
    promotion_min_subjects = models.IntegerField(default=5, help_text='Minimum subjects to pass for promotion')
    
    # Communication Settings
    sms_enabled = models.BooleanField(default=False)
    email_enabled = models.BooleanField(default=True)
    notification_enabled = models.BooleanField(default=True)
    
    # Bank Details
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)
    bank_swift_code = models.CharField(max_length=20, blank=True)
    mobile_money_enabled = models.BooleanField(default=False)
    mobile_money_number = models.CharField(max_length=20, blank=True)
    mobile_money_name = models.CharField(max_length=50, blank=True, help_text='MTN, Airtel, etc.')
    
    # Additional Settings (JSON for flexibility)
    custom_settings = models.JSONField(default=dict, blank=True, help_text='Store any additional custom settings')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'School Settings'
        verbose_name_plural = 'School Settings'
    
    def __str__(self):
        return f"Settings for {self.school.name}"
    
    def get_setting(self, key, default=None):
        """Get a custom setting value"""
        return self.custom_settings.get(key, default)
    
    def set_setting(self, key, value):
        """Set a custom setting value"""
        self.custom_settings[key] = value
        self.save()


class GradingScale(TenantAwareModel):
    """
    Configurable grading scales per school
    Supports percentage, GPA, letter grades, or custom
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='grading_scales', db_index=True)
    name = models.CharField(max_length=100, help_text='e.g., Primary Scale, O-Level Scale, University Scale')
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'name']
        ordering = ['school', 'name']
    
    def __str__(self):
        return f"{self.school.code} - {self.name}"


class GradingScaleRange(TenantAwareModel):
    """
    Individual grade ranges within a grading scale
    Completely configurable - no hardcoded grades
    """
    grading_scale = models.ForeignKey(GradingScale, on_delete=models.CASCADE, related_name='ranges')
    
    # Grade Definition
    grade = models.CharField(max_length=10, help_text='A+, A, B, 1st Class, Distinction, etc.')
    min_mark = models.DecimalField(max_digits=5, decimal_places=2)
    max_mark = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Optional Details
    gpa_value = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    description = models.CharField(max_length=100, blank=True, help_text='Excellent, Good, Pass, Fail, etc.')
    color_code = models.CharField(max_length=7, blank=True, help_text='Hex color for reports')
    is_passing = models.BooleanField(default=True)
    
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['grading_scale', '-min_mark']
        unique_together = ['grading_scale', 'grade']
    
    def __str__(self):
        return f"{self.grade} ({self.min_mark}-{self.max_mark})"


class ExamType(TenantAwareModel):
    """
    Configurable exam types per school
    No hardcoded exam types
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='exam_types', db_index=True)
    name = models.CharField(max_length=100, help_text='Midterm, Final, Quiz, Assignment, CAT, etc.')
    code = models.CharField(max_length=20, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=100.00, help_text='Percentage weight in final grade')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['school', 'name']
        ordering = ['school', 'order']
    
    def __str__(self):
        return f"{self.school.code} - {self.name}"


class UserRoleDefinition(TenantAwareModel):
    """
    Configurable user roles per school
    Schools can define their own roles beyond the basic ones
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='custom_roles', db_index=True)
    name = models.CharField(max_length=50, help_text='e.g., Head of Department, Subject Coordinator')
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=dict, help_text='Store role permissions')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'code']
        ordering = ['school', 'name']
    
    def __str__(self):
        return f"{self.school.code} - {self.name}"


class MessageTemplate(TenantAwareModel):
    """
    Configurable message templates per school
    SMS, Email, Notification templates - all customizable
    """
    TEMPLATE_TYPE_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('notification', 'In-App Notification'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='message_templates', db_index=True)
    name = models.CharField(max_length=100, help_text='e.g., Fee Reminder, Exam Results, Absence Alert')
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES)
    
    # Template Content
    subject = models.CharField(max_length=200, blank=True, help_text='For email only')
    body = models.TextField(help_text='Use {variable_name} for placeholders')
    
    # Metadata
    variables = models.JSONField(default=list, help_text='List of available variables')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'name', 'template_type']
        ordering = ['school', 'template_type', 'name']
    
    def __str__(self):
        return f"{self.school.code} - {self.name} ({self.template_type})"
    
    def render(self, context):
        """Render template with context variables"""
        content = self.body
        for key, value in context.items():
            content = content.replace(f'{{{key}}}', str(value))
        return content


class StudentCategory(TenantAwareModel):
    """
    Configurable student categories per school
    Day, Boarding, Scholarship, International, etc. - all configurable
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='student_categories', db_index=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    
    # Fee implications
    has_different_fees = models.BooleanField(default=False)
    fee_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, help_text='Multiply base fees by this')
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['school', 'code']
        ordering = ['school', 'name']
        verbose_name_plural = 'Student Categories'
    
    def __str__(self):
        return f"{self.school.code} - {self.name}"


class AdmissionRequirement(TenantAwareModel):
    """
    Configurable admission requirements per school and level
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='admission_requirements', db_index=True)
    level_name = models.CharField(max_length=100, help_text='Which level/grade this applies to')
    
    requirement_name = models.CharField(max_length=200)
    description = models.TextField()
    is_mandatory = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['school', 'level_name', 'order']
    
    def __str__(self):
        return f"{self.school.code} - {self.level_name}: {self.requirement_name}"
