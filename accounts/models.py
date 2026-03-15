from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import Department

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'System Administrator'),
        ('registrar', 'Registrar'),  # For universities/colleges - handles exams
        ('director', 'Director'),
        ('dos', 'Director of Studies (DOS)'),  # For schools - handles exams
        ('head_of_class', 'Head of Class'),
        ('teacher', 'Teacher'),
        ('security', 'Security'),
        ('bursar', 'Bursar'),
        ('accountant', 'Accountant'),
        ('hr_manager', 'HR Manager'),
        ('receptionist', 'Receptionist'),
        ('librarian', 'Librarian'),
        ('nurse', 'Nurse'),
        ('parent', 'Parent'),
        ('student', 'Student'),
        ('staff', 'Staff'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    hire_date = models.DateField(null=True, blank=True)
    is_active_employee = models.BooleanField(default=True)
    force_password_reset = models.BooleanField(default=False, help_text='Force user to reset password on next login')
    
    # For Head of Class and Teachers
    class_name = models.CharField(max_length=100, blank=True, help_text='Class assigned to Head of Class or Teacher (e.g., Grade 1A, Grade 2B)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active_employee']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"
    
    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'pk': self.pk})
    
    @property
    def is_director(self):
        return self.role == 'director'
    
    @property
    def is_dos(self):
        """Director of Studies - handles exams in schools"""
        return self.role == 'dos'
    
    @property
    def is_registrar(self):
        """Registrar - handles exams in universities/colleges"""
        return self.role == 'registrar'
    
    @property
    def is_teacher(self):
        return self.role == 'teacher'
    
    @property
    def is_head_of_class(self):
        return self.role == 'head_of_class'
    
    @property
    def is_security(self):
        return self.role == 'security'
    
    @property
    def is_accountant(self):
        return self.role == 'accountant'
    
    @property
    def is_bursar(self):
        return self.role == 'bursar'
    
    @property
    def can_manage_exams(self):
        """Check if user can manage examinations based on institution type"""
        from .school_config import get_school_config
        config = get_school_config()
        
        if not config:
            return self.role == 'admin'
        
        # For schools (nursery, primary, secondary): DOS manages exams
        if config.school_type in ['nursery', 'primary', 'secondary', 'combined']:
            return self.role in ['admin', 'dos']
        
        # For universities/colleges: Registrar manages exams
        elif config.school_type in ['university', 'college']:
            return self.role in ['admin', 'registrar']
        
        return self.role == 'admin'
    
    @property
    def can_manage_fees(self):
        return self.role in ['admin', 'director', 'bursar', 'accountant']
    
    @property
    def can_manage_employees(self):
        return self.role in ['admin', 'director', 'hr_manager']
    
    @property
    def can_view_reports(self):
        return self.role in ['admin', 'director', 'dos', 'registrar', 'accountant', 'hr_manager']



# Import audit models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class AuditLog(models.Model):
    """Track all important system actions"""
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('payment', 'Payment Recorded'),
        ('view', 'Viewed'),
        ('export', 'Exported'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    # Generic relation to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Details
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"


class LoginLog(models.Model):
    """Track login attempts"""
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('blocked', 'Blocked'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='login_logs')
    username_attempted = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['status', '-timestamp']),
            models.Index(fields=['-timestamp']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.username_attempted} - {self.status} - {self.timestamp}"


# Import SchoolConfiguration
from .school_config import SchoolConfiguration



class Parent(models.Model):
    """Parent/Guardian account"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    national_id = models.CharField(max_length=50, blank=True)
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__last_name', 'user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} (Parent)"
    
    def get_children(self):
        """Get all children linked to this parent"""
        return self.children.all()


class ParentStudentLink(models.Model):
    """Link between parent and student"""
    RELATIONSHIP_CHOICES = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('guardian', 'Legal Guardian'),
        ('grandfather', 'Grandfather'),
        ('grandmother', 'Grandmother'),
        ('uncle', 'Uncle'),
        ('aunt', 'Aunt'),
        ('sibling', 'Sibling'),
        ('other', 'Other'),
    ]
    
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='children')
    student = models.ForeignKey('core.Student', on_delete=models.CASCADE, related_name='parents')
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    is_primary_contact = models.BooleanField(default=False, help_text='Primary contact for this student')
    can_pickup = models.BooleanField(default=True, help_text='Authorized to pick up student')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['parent', 'student']
        ordering = ['-is_primary_contact', 'relationship']
    
    def __str__(self):
        return f"{self.parent.user.get_full_name()} - {self.student.get_full_name()} ({self.relationship})"


class ParentTeacherMessage(models.Model):
    """Messaging system between parents and teachers"""
    SENDER_TYPE_CHOICES = [
        ('parent', 'Parent'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]
    
    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('replied', 'Replied'),
    ]
    
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPE_CHOICES)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    
    recipient_type = models.CharField(max_length=10, choices=SENDER_TYPE_CHOICES)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    
    student = models.ForeignKey('core.Student', on_delete=models.CASCADE, related_name='messages', help_text='Student this message is about')
    
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unread')
    
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', help_text='Reply to this message')
    
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['student', '-sent_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.get_full_name()} to {self.recipient.get_full_name()} - {self.subject}"
    
    def mark_as_read(self):
        """Mark message as read"""
        if self.status == 'unread':
            from django.utils import timezone
            self.status = 'read'
            self.read_at = timezone.now()
            self.save()
