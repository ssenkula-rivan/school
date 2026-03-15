from django.contrib import admin
from .models import BookCategory, Book, BookBorrow, BookReservation, LibraryMember


@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['accession_number', 'title', 'author', 'category', 'total_copies', 'available_copies', 'status']
    list_filter = ['status', 'category', 'language', 'publication_year']
    search_fields = ['isbn', 'title', 'author', 'accession_number', 'keywords']
    readonly_fields = ['added_at', 'updated_at']
    
    fieldsets = (
        ('Book Information', {
            'fields': ('isbn', 'title', 'author', 'publisher', 'publication_year', 'edition')
        }),
        ('Classification', {
            'fields': ('category', 'language', 'keywords')
        }),
        ('Physical Details', {
            'fields': ('pages', 'cover_image', 'description')
        }),
        ('Library Management', {
            'fields': ('accession_number', 'shelf_location', 'total_copies', 'available_copies', 'status')
        }),
        ('Pricing', {
            'fields': ('price', 'replacement_cost')
        }),
    )


@admin.register(BookBorrow)
class BookBorrowAdmin(admin.ModelAdmin):
    list_display = ['student', 'book', 'borrow_date', 'due_date', 'return_date', 'status', 'fine_amount', 'fine_paid']
    list_filter = ['status', 'fine_paid', 'borrow_date', 'due_date']
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_number', 'book__title']
    date_hierarchy = 'borrow_date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Borrow Information', {
            'fields': ('book', 'student', 'borrow_date', 'due_date', 'return_date', 'status')
        }),
        ('Fine Management', {
            'fields': ('fine_amount', 'fine_paid', 'fine_paid_date')
        }),
        ('Staff', {
            'fields': ('issued_by', 'returned_to')
        }),
        ('Condition & Notes', {
            'fields': ('condition_on_borrow', 'condition_on_return', 'remarks')
        }),
    )
    
    actions = ['calculate_fines', 'mark_returned']
    
    def calculate_fines(self, request, queryset):
        total_fine = 0
        for borrow in queryset:
            fine = borrow.calculate_fine()
            total_fine += fine
        self.message_user(request, f'Calculated fines for {queryset.count()} records. Total: {total_fine}')
    calculate_fines.short_description = 'Calculate fines for overdue books'
    
    def mark_returned(self, request, queryset):
        count = 0
        for borrow in queryset.filter(status='active'):
            borrow.return_book(request.user)
            count += 1
        self.message_user(request, f'{count} books marked as returned.')
    mark_returned.short_description = 'Mark selected books as returned'


@admin.register(BookReservation)
class BookReservationAdmin(admin.ModelAdmin):
    list_display = ['student', 'book', 'reservation_date', 'expiry_date', 'status']
    list_filter = ['status', 'reservation_date']
    search_fields = ['student__first_name', 'student__last_name', 'book__title']
    date_hierarchy = 'reservation_date'


@admin.register(LibraryMember)
class LibraryMemberAdmin(admin.ModelAdmin):
    list_display = ['membership_number', 'student', 'status', 'current_books_borrowed', 'max_books_allowed', 'outstanding_fines']
    list_filter = ['status', 'join_date']
    search_fields = ['membership_number', 'student__first_name', 'student__last_name', 'student__admission_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Member Information', {
            'fields': ('student', 'membership_number', 'join_date', 'expiry_date', 'status')
        }),
        ('Borrowing Limits', {
            'fields': ('max_books_allowed', 'current_books_borrowed')
        }),
        ('Statistics', {
            'fields': ('total_books_borrowed', 'total_fines_paid', 'outstanding_fines')
        }),
    )
