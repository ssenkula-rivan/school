from django.contrib import admin
from .models import AccountType, Account, Transaction, JournalEntry, Receipt

class JournalEntryInline(admin.TabularInline):
    model = JournalEntry
    extra = 2  # Shows 2 empty forms by default

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    inlines = [JournalEntryInline]
    list_display = ('date', 'description', 'reference_number')

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('date', 'receipt_type', 'vendor', 'student_name', 'amount', 'category', 'user')
    list_filter = ('receipt_type', 'category', 'date', 'user', 'school_year')
    search_fields = ('vendor', 'description', 'student_name', 'grade_class')
    date_hierarchy = 'date'
    fieldsets = (
        ('Receipt Type', {
            'fields': ('receipt_type',)
        }),
        ('Basic Information', {
            'fields': ('user', 'vendor', 'amount', 'date', 'category')
        }),
        ('Details', {
            'fields': ('description', 'receipt_image', 'transaction')
        }),
        ('School Information', {
            'fields': ('student_name', 'grade_class', 'school_year'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(AccountType)
admin.site.register(Account)
