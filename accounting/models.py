# accounting/models.py
from django.db import models
from django.contrib.auth.models import User
from core.models import School

class AccountType(models.Model):
    """Asset, Liability, Equity, Revenue, Expense"""
    name = models.CharField(max_length=50)
    normal_balance = models.CharField(max_length=6, choices=[
        ('DEBIT', 'Debit'),
        ('CREDIT', 'Credit')
    ])

    def __str__(self):
        return self.name

class Account(models.Model):
    """Chart of Accounts"""
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    account_type = models.ForeignKey(AccountType, on_delete=models.PROTECT)
    account_number = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ['school', 'account_number']

    def __str__(self):
        return f"{self.account_number} - {self.name}"

class Transaction(models.Model):
    """Double-entry transaction"""
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=200)
    reference_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.date} - {self.description}"

class JournalEntry(models.Model):
    """Individual debit/credit entries"""
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='entries')
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    entry_type = models.CharField(max_length=6, choices=[
        ('DEBIT', 'Debit'),
        ('CREDIT', 'Credit')
    ])

    class Meta:
        verbose_name_plural = "Journal Entries"

    def __str__(self):
        return f"{self.account.name} - {self.entry_type}: ${self.amount}"

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
        ('OVERDUE', 'Overdue'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UNPAID')
    created_at = models.DateField(auto_now_add=True)
    scanned_copy = models.ImageField(upload_to='scanned_invoices/', blank=True, null=True)

    def __str__(self):
        return f"{self.client} - {self.amount} - {self.status}"

class Receipt(models.Model):
    RECEIPT_TYPE_CHOICES = [
        ('SALES', 'Sales Receipt'),
        ('PAYMENT', 'Payment Receipt (Receive Payment)'),
        ('STUDENT_FEES', 'Payment Receipt (Student Fees)'),
        ('EXPENSE', 'Expense Receipt'),
        ('REFUND', 'Refund Receipt'),
        ('BILL_PAYMENT', 'Bill Payment Receipt'),
    ]
    
    CATEGORY_CHOICES = [
        ('OFFICE', 'Office Supplies'),
        ('TRAVEL', 'Travel & Transportation'),
        ('MEALS', 'Meals & Entertainment'),
        ('UTILITIES', 'Utilities'),
        ('RENT', 'Rent'),
        ('EQUIPMENT', 'Equipment'),
        ('SERVICES', 'Professional Services'),
        ('TUITION', 'Tuition Fees'),
        ('BOOKS', 'Books & Educational Materials'),
        ('SCHOOL_SUPPLIES', 'School Supplies'),
        ('UNIFORMS', 'Uniforms & Clothing'),
        ('SPORTS', 'Sports & Athletics'),
        ('FIELD_TRIPS', 'Field Trips & Excursions'),
        ('LAB_FEES', 'Laboratory Fees'),
        ('TECHNOLOGY', 'Technology & Computer'),
        ('MUSIC_ARTS', 'Music & Arts Programs'),
        ('AFTER_SCHOOL', 'After School Programs'),
        ('LUNCH', 'School Lunch & Cafeteria'),
        ('TRANSPORTATION', 'School Transportation'),
        ('FUNDRAISING', 'Fundraising Expenses'),
        ('FACILITY', 'Facility & Maintenance'),
        ('STAFF_TRAINING', 'Staff Training & Development'),
        ('OTHER', 'Other'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='receipts')
    
    receipt_type = models.CharField(max_length=20, choices=RECEIPT_TYPE_CHOICES, default='EXPENSE')
    vendor = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    description = models.TextField(blank=True)
    receipt_image = models.ImageField(upload_to='receipts/', blank=True, null=True)
    
    student_name = models.CharField(max_length=200, blank=True, help_text="Student name (for school expenses)")
    grade_class = models.CharField(max_length=50, blank=True, help_text="Grade or class")
    school_year = models.CharField(max_length=20, blank=True, help_text="e.g., 2024-2025")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.get_receipt_type_display()} - {self.vendor} - ${self.amount} - {self.date}"
