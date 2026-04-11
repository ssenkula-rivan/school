"""
Budget Planning and Visitor Tracking Models
Helps schools plan expenses for future terms and track visitors
"""
from django.db import models
from django.contrib.auth.models import User
from .models import School, AcademicYear
from decimal import Decimal


class Budget(models.Model):
    """School budget planning for terms/years"""
    
    BUDGET_TYPE_CHOICES = [
        ('annual', 'Annual Budget'),
        ('term', 'Term Budget'),
        ('quarterly', 'Quarterly Budget'),
        ('monthly', 'Monthly Budget'),
        ('project', 'Project Budget'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Approval'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('revised', 'Revised'),
    ]
    
    # Multi-tenant
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='budgets')
    
    # Budget Details
    budget_number = models.CharField(max_length=50, unique=True, db_index=True)
    budget_type = models.CharField(max_length=20, choices=BUDGET_TYPE_CHOICES)
    title = models.CharField(max_length=200, help_text='e.g., Term 1 Budget 2024, Annual Budget 2024')
    description = models.TextField(blank=True)
    
    # Period
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Financial
    total_budget = models.DecimalField(max_digits=15, decimal_places=2, help_text='Total planned budget')
    total_spent = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text='Total amount spent')
    total_committed = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text='Committed but not yet spent')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)
    
    # Approval
    prepared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='prepared_budgets')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_budgets')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date', '-created_at']
        indexes = [
            models.Index(fields=['school', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.budget_number} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.budget_number:
            from django.utils import timezone
            year = self.start_date.year if self.start_date else timezone.now().year
            count = Budget.objects.filter(school=self.school, start_date__year=year).count() + 1
            self.budget_number = f"BUD-{self.school.code}-{year}-{count:04d}"
        super().save(*args, **kwargs)
    
    @property
    def remaining_budget(self):
        """Calculate remaining budget"""
        return self.total_budget - self.total_spent - self.total_committed
    
    @property
    def utilization_percentage(self):
        """Calculate budget utilization percentage"""
        if self.total_budget == 0:
            return 0
        return (self.total_spent / self.total_budget) * 100
    
    def approve(self, approved_by_user):
        """Approve the budget"""
        from django.utils import timezone
        self.status = 'approved'
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        self.save()


class BudgetLine(models.Model):
    """Individual budget line items"""
    
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='line_items')
    
    # Category
    category = models.CharField(max_length=100, help_text='e.g., Salaries, Utilities, Workshops')
    subcategory = models.CharField(max_length=100, blank=True, help_text='e.g., Teacher Salaries, Electricity')
    description = models.TextField()
    
    # Financial
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text='Budgeted amount')
    spent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Amount spent')
    committed_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Committed amount')
    
    # Priority
    priority = models.IntegerField(default=3, help_text='1=High, 2=Medium, 3=Low')
    is_essential = models.BooleanField(default=True, help_text='Essential expense')
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', 'category']
    
    def __str__(self):
        return f"{self.category} - {self.subcategory} - UGX {self.allocated_amount:,.0f}"
    
    @property
    def remaining_amount(self):
        """Calculate remaining amount"""
        return self.allocated_amount - self.spent_amount - self.committed_amount
    
    @property
    def utilization_percentage(self):
        """Calculate utilization percentage"""
        if self.allocated_amount == 0:
            return 0
        return (self.spent_amount / self.allocated_amount) * 100


class Visitor(models.Model):
    """Track school visitors for security and expense tracking"""
    
    VISITOR_TYPE_CHOICES = [
        ('parent', 'Parent/Guardian'),
        ('vendor', 'Vendor/Supplier'),
        ('contractor', 'Contractor'),
        ('inspector', 'Government Inspector'),
        ('guest_speaker', 'Guest Speaker'),
        ('workshop_facilitator', 'Workshop Facilitator'),
        ('maintenance', 'Maintenance Personnel'),
        ('delivery', 'Delivery Person'),
        ('official', 'Official Visitor'),
        ('other', 'Other'),
    ]
    
    PURPOSE_CHOICES = [
        ('meeting', 'Meeting'),
        ('delivery', 'Delivery'),
        ('maintenance', 'Maintenance/Repair'),
        ('workshop', 'Workshop/Training'),
        ('inspection', 'Inspection'),
        ('event', 'Event/Program'),
        ('consultation', 'Consultation'),
        ('other', 'Other'),
    ]
    
    # Multi-tenant
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='visitors')
    
    # Visitor Information
    visitor_number = models.CharField(max_length=50, unique=True, db_index=True)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    id_number = models.CharField(max_length=50, blank=True, help_text='ID/Passport number')
    company = models.CharField(max_length=200, blank=True, help_text='Company/Organization')
    
    # Visit Details
    visitor_type = models.CharField(max_length=30, choices=VISITOR_TYPE_CHOICES)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    purpose_details = models.TextField(help_text='Detailed purpose of visit')
    
    # Person to meet
    person_to_meet = models.CharField(max_length=200, help_text='Staff member or department')
    
    # Timing
    visit_date = models.DateField(db_index=True)
    check_in_time = models.DateTimeField(help_text='Actual check-in time')
    expected_checkout_time = models.TimeField(blank=True, null=True)
    check_out_time = models.DateTimeField(null=True, blank=True, help_text='Actual check-out time')
    
    # Security
    checked_in_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='checked_in_visitors',
        help_text='Security who checked in visitor'
    )
    checked_out_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checked_out_visitors',
        help_text='Security who checked out visitor'
    )
    
    # Expenses (if applicable)
    has_expense = models.BooleanField(default=False, help_text='Visit resulted in expense')
    expense_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expense_description = models.TextField(blank=True)
    
    # Items brought in/out
    items_brought_in = models.TextField(blank=True, help_text='Items/equipment brought in')
    items_taken_out = models.TextField(blank=True, help_text='Items taken out')
    
    # Status
    is_checked_out = models.BooleanField(default=False, db_index=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-visit_date', '-check_in_time']
        indexes = [
            models.Index(fields=['school', 'visit_date']),
            models.Index(fields=['visitor_type']),
            models.Index(fields=['is_checked_out']),
        ]
    
    def __str__(self):
        return f"{self.visitor_number} - {self.full_name} - {self.visit_date}"
    
    def save(self, *args, **kwargs):
        if not self.visitor_number:
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            count = Visitor.objects.filter(
                school=self.school,
                visit_date=timezone.now().date()
            ).count() + 1
            self.visitor_number = f"VIS-{self.school.code}-{date_str}-{count:04d}"
        super().save(*args, **kwargs)
    
    def check_out(self, checked_out_by_user):
        """Check out visitor"""
        from django.utils import timezone
        self.check_out_time = timezone.now()
        self.checked_out_by = checked_out_by_user
        self.is_checked_out = True
        self.save()


class WorkshopExpense(models.Model):
    """Track workshop and training expenses"""
    
    # Multi-tenant
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='workshop_expenses')
    
    # Workshop Details
    workshop_number = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Participants
    target_participants = models.CharField(max_length=200, help_text='e.g., Teachers, Students, Parents')
    expected_attendees = models.IntegerField(help_text='Expected number of attendees')
    actual_attendees = models.IntegerField(null=True, blank=True, help_text='Actual number of attendees')
    
    # Facilitator
    facilitator_name = models.CharField(max_length=200)
    facilitator_phone = models.CharField(max_length=20, blank=True)
    facilitator_email = models.EmailField(blank=True)
    facilitator_fee = models.DecimalField(max_digits=10, decimal_places=2, help_text='Facilitator payment')
    
    # Expenses
    venue_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    materials_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refreshments_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Budget
    budget_line = models.ForeignKey(BudgetLine, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Tracking
    organized_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='organized_workshops')
    
    # Status
    is_completed = models.BooleanField(default=False)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['school', 'start_date']),
        ]
    
    def __str__(self):
        return f"{self.workshop_number} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.workshop_number:
            from django.utils import timezone
            year = self.start_date.year if self.start_date else timezone.now().year
            count = WorkshopExpense.objects.filter(
                school=self.school,
                start_date__year=year
            ).count() + 1
            self.workshop_number = f"WS-{self.school.code}-{year}-{count:04d}"
        super().save(*args, **kwargs)
    
    @property
    def total_cost(self):
        """Calculate total workshop cost"""
        return (
            self.facilitator_fee +
            self.venue_cost +
            self.materials_cost +
            self.refreshments_cost +
            self.transport_cost +
            self.other_costs
        )
    
    @property
    def cost_per_attendee(self):
        """Calculate cost per attendee"""
        attendees = self.actual_attendees or self.expected_attendees
        if attendees == 0:
            return 0
        return self.total_cost / attendees
