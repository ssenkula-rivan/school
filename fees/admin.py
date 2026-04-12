from django.contrib import admin
from .models import FeeStructure, FeePayment, FeeBalance, StudentDiscipline, StudentIDCard


class SchoolFilteredAdmin(admin.ModelAdmin):
    """Base admin class that filters by school for non-superusers"""
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Filter by user's school
        try:
            user_school = request.user.userprofile.school
            return qs.filter(school=user_school)
        except:
            return qs.none()
    
    def has_add_permission(self, request):
        # School admins can add
        return request.user.is_staff
    
    def has_change_permission(self, request, obj=None):
        # School admins can edit their own school's data
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        try:
            user_school = request.user.userprofile.school
            return obj.school == user_school
        except:
            return False
    
    def has_delete_permission(self, request, obj=None):
        # School admins can delete their own school's data
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        try:
            user_school = request.user.userprofile.school
            return obj.school == user_school
        except:
            return False


class StudentRelatedAdmin(admin.ModelAdmin):
    """Base admin class for models related to Student (which has school FK)"""
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Filter by user's school through student relationship
        try:
            user_school = request.user.userprofile.school
            return qs.filter(student__school=user_school)
        except:
            return qs.none()
    
    def has_add_permission(self, request):
        return request.user.is_staff
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        try:
            user_school = request.user.userprofile.school
            return obj.student.school == user_school
        except:
            return False
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        try:
            user_school = request.user.userprofile.school
            return obj.student.school == user_school
        except:
            return False


@admin.register(FeeStructure)
class FeeStructureAdmin(SchoolFilteredAdmin):
    list_display = ['academic_year', 'grade', 'term', 'total_fee', 'is_active']
    list_filter = ['academic_year', 'grade', 'term', 'is_active']
    search_fields = ['grade__name', 'academic_year__name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('school', 'academic_year', 'grade', 'term', 'is_active', 'description')
        }),
        ('Fee Components', {
            'fields': ('tuition_fee', 'registration_fee', 'library_fee', 'sports_fee',
                      'lab_fee', 'transport_fee', 'uniform_fee', 'exam_fee', 'other_fee')
        }),
    )


@admin.register(FeePayment)
class FeePaymentAdmin(SchoolFilteredAdmin):
    list_display = ['receipt_number', 'student', 'amount_paid', 'payment_date', 
                   'payment_method', 'payment_status', 'received_by']
    list_filter = ['payment_status', 'payment_method', 'payment_date']
    search_fields = ['receipt_number', 'student__admission_number', 'student__first_name', 
                    'student__last_name', 'transaction_reference']
    date_hierarchy = 'payment_date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(FeeBalance)
class FeeBalanceAdmin(SchoolFilteredAdmin):
    list_display = ['student', 'fee_structure', 'total_fee', 'amount_paid', 'balance', 'is_paid']
    list_filter = ['is_paid', 'fee_structure__academic_year', 'fee_structure__grade']
    search_fields = ['student__admission_number', 'student__first_name', 'student__last_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(StudentDiscipline)
class StudentDisciplineAdmin(StudentRelatedAdmin):
    list_display = ['student', 'incident_date', 'incident_type', 'action_taken', 'resolved', 'parent_notified']
    list_filter = ['incident_type', 'action_taken', 'resolved', 'parent_notified', 'incident_date']
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_number', 'description']
    date_hierarchy = 'incident_date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Incident Information', {
            'fields': ('student', 'incident_date', 'incident_type', 'description', 'location')
        }),
        ('Action Taken', {
            'fields': ('action_taken', 'action_details', 'start_date', 'end_date')
        }),
        ('Parent Communication', {
            'fields': ('parent_notified', 'parent_notified_date', 'parent_response')
        }),
        ('Resolution', {
            'fields': ('resolved', 'resolution_notes', 'reported_by')
        }),
    )


@admin.register(StudentIDCard)
class StudentIDCardAdmin(StudentRelatedAdmin):
    list_display = ['card_number', 'student', 'issue_date', 'expiry_date', 'status', 'is_valid']
    list_filter = ['status', 'issue_date', 'expiry_date']
    search_fields = ['card_number', 'student__first_name', 'student__last_name', 'student__admission_number']
    date_hierarchy = 'issue_date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Card Information', {
            'fields': ('student', 'card_number', 'issue_date', 'expiry_date', 'status')
        }),
        ('Identification', {
            'fields': ('barcode', 'qr_code')
        }),
        ('Issuance Details', {
            'fields': ('issued_by', 'replacement_reason', 'replacement_fee_paid')
        }),
    )
    
    actions = ['mark_as_expired', 'mark_as_lost']
    
    def mark_as_expired(self, request, queryset):
        queryset.update(status='expired')
        self.message_user(request, f'{queryset.count()} ID cards marked as expired.')
    mark_as_expired.short_description = 'Mark selected ID cards as expired'
    
    def mark_as_lost(self, request, queryset):
        queryset.update(status='lost')
        self.message_user(request, f'{queryset.count()} ID cards marked as lost.')
    mark_as_lost.short_description = 'Mark selected ID cards as lost'
