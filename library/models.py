from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from core.models import Student
from decimal import Decimal
from datetime import timedelta


class BookCategory(models.Model):
    """
    Book categories/genres
    
    TENANT ISOLATION: Global categories (no school FK)
    Shared across all schools - not tenant-specific
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Book Categories'
    
    def __str__(self):
        return self.name


class Book(models.Model):
    """
    Library book catalog
    
    TENANT ISOLATION: Global books (no school FK)
    Shared catalog across schools - borrowing is tenant-specific via Student
    """
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('reserved', 'Reserved'),
        ('damaged', 'Damaged'),
        ('lost', 'Lost'),
        ('under_repair', 'Under Repair'),
    ]
    
    # Book Information
    isbn = models.CharField(max_length=13, unique=True, help_text='ISBN-13 number')
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200, blank=True)
    publication_year = models.IntegerField(null=True, blank=True)
    edition = models.CharField(max_length=50, blank=True)
    
    # Classification
    category = models.ForeignKey(BookCategory, on_delete=models.SET_NULL, null=True, related_name='books')
    language = models.CharField(max_length=50, default='English')
    
    # Physical Details
    pages = models.IntegerField(null=True, blank=True)
    cover_image = models.ImageField(upload_to='library/covers/', blank=True, null=True)
    
    # Library Management
    accession_number = models.CharField(max_length=50, unique=True, help_text='Library catalog number')
    shelf_location = models.CharField(max_length=100, blank=True, help_text='Shelf/rack location')
    total_copies = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    available_copies = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    replacement_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Cost if book is lost')
    
    # Additional Info
    description = models.TextField(blank=True)
    keywords = models.CharField(max_length=500, blank=True, help_text='Search keywords')
    
    # System fields
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='added_books')
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['isbn']),
            models.Index(fields=['accession_number']),
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.accession_number} - {self.title}"
    
    def is_available(self):
        """Check if book is available for borrowing"""
        return self.status == 'available' and self.available_copies > 0


class BookBorrow(models.Model):
    """
    Book borrowing records
    
    TENANT ISOLATION: Indirect via Student (has school FK)
    Automatically filtered when querying through Student relationship
    
    CRITICAL SECURITY:
    - Uses PROTECT on ForeignKeys to prevent accidental deletion
    - Locks records during return to prevent race conditions
    - Validates book availability before borrowing
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('lost', 'Lost'),
    ]
    
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='borrow_records')
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name='borrowed_books')
    
    # Borrow Details
    borrow_date = models.DateField(db_index=True)
    due_date = models.DateField(db_index=True)
    return_date = models.DateField(null=True, blank=True, db_index=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Fine Management
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fine_paid = models.BooleanField(default=False)
    fine_paid_date = models.DateField(null=True, blank=True)
    
    # Staff
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issued_books')
    returned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_books')
    
    # Notes
    remarks = models.TextField(blank=True)
    condition_on_borrow = models.CharField(max_length=100, default='Good', help_text='Book condition when borrowed')
    condition_on_return = models.CharField(max_length=100, blank=True, help_text='Book condition when returned')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-borrow_date']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['book', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.book.title}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate book is available (only on creation)
        if self.pk is None and not self.book.is_available():
            raise ValidationError(f'Book "{self.book.title}" is not available for borrowing')
        
        # Validate due date is after borrow date
        if self.due_date <= self.borrow_date:
            raise ValidationError('Due date must be after borrow date')
        
        # Validate student can borrow
        if hasattr(self.student, 'library_membership'):
            membership = self.student.library_membership
            if not membership.can_borrow():
                raise ValidationError(f'Student cannot borrow books. Status: {membership.get_status_display()}')
    
    def save(self, *args, **kwargs):
        if self.pk is None:
            self.full_clean()
        super().save(*args, **kwargs)
    
    def calculate_fine(self, fine_per_day=Decimal('100.00')):
        """Calculate fine for overdue books"""
        if self.status == 'returned' or not self.is_overdue():
            return Decimal('0.00')
        
        from datetime import date
        today = date.today()
        days_overdue = (today - self.due_date).days
        
        if days_overdue > 0:
            self.fine_amount = Decimal(days_overdue) * fine_per_day
            self.status = 'overdue'
            self.save()
            return self.fine_amount
        
        return Decimal('0.00')
    
    def is_overdue(self):
        """Check if book is overdue"""
        from datetime import date
        if self.status == 'returned':
            return False
        return date.today() > self.due_date
    
    def days_overdue(self):
        """Get number of days overdue"""
        if not self.is_overdue():
            return 0
        from datetime import date
        return (date.today() - self.due_date).days
    
    def return_book(self, returned_by, condition='Good'):
        """Process book return"""
        from datetime import date
        from django.db import transaction
        
        with transaction.atomic():
            # Lock both records to prevent race conditions
            borrow = BookBorrow.objects.select_for_update().get(pk=self.pk)
            book = Book.objects.select_for_update().get(pk=borrow.book_id)
            
            borrow.return_date = date.today()
            borrow.returned_to = returned_by
            borrow.condition_on_return = condition
            borrow.status = 'returned'
            
            # Calculate any outstanding fine
            if borrow.is_overdue():
                borrow.calculate_fine()
            
            # Update book availability
            book.available_copies += 1
            if book.available_copies > 0:
                book.status = 'available'
            book.save()
            
            borrow.save()


class BookReservation(models.Model):
    """
    Book reservation system
    
    TENANT ISOLATION: Indirect via Student (has school FK)
    Automatically filtered when querying through Student relationship
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='book_reservations')
    
    reservation_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField(help_text='Reservation expires after this date')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    fulfilled_date = models.DateField(null=True, blank=True)
    fulfilled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='fulfilled_reservations')
    
    remarks = models.TextField(blank=True)
    
    class Meta:
        ordering = ['reservation_date']
        indexes = [
            models.Index(fields=['book', 'status']),
            models.Index(fields=['student', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.book.title} ({self.status})"


class LibraryMember(models.Model):
    """
    Library membership for students
    
    TENANT ISOLATION: Indirect via Student (has school FK)
    Automatically filtered when querying through Student relationship
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
    ]
    
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='library_membership')
    membership_number = models.CharField(max_length=50, unique=True)
    
    join_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    max_books_allowed = models.IntegerField(default=3, help_text='Maximum books that can be borrowed at once')
    current_books_borrowed = models.IntegerField(default=0)
    
    total_books_borrowed = models.IntegerField(default=0, help_text='Lifetime total')
    total_fines_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    outstanding_fines = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['membership_number']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.membership_number}"
    
    def can_borrow(self):
        """Check if member can borrow more books"""
        return (self.status == 'active' and 
                self.current_books_borrowed < self.max_books_allowed and
                self.outstanding_fines == 0)
