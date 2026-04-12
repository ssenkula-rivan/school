from django.contrib import admin
from .models import (
    School, Department, AcademicYear, Grade, Student,
    GatePass, Expense, Budget, BudgetLine, Visitor, WorkshopExpense
)


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
    
    def save_model(self, request, obj, form, change):
        """Auto-assign school when saving"""
        if not request.user.is_superuser:
            try:
                if hasattr(obj, 'school') and not obj.school_id:
                    obj.school = request.user.userprofile.school
            except Exception:
                pass
        super().save_model(request, obj, form, change)
    
    def has_module_permission(self, request):
        """Allow school admins to see the module"""
        return request.user.is_active and request.user.is_staff
    
    def has_view_permission(self, request, obj=None):
        """Allow school admins to view"""
        return request.user.is_active and request.user.is_staff
    
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


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'school_type', 'curriculum', 'is_active', 'subscription_end']
    list_filter = ['is_active', 'school_type', 'institution_type', 'curriculum']
    search_fields = ['name', 'code', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # School admins can only see their own school
        try:
            user_school = request.user.userprofile.school
            return qs.filter(id=user_school.id)
        except:
            return qs.none()
    
    def has_add_permission(self, request):
        # Only superusers can add schools
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete schools
        return request.user.is_superuser
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'school_type', 'institution_type', 'email', 'email_domain', 'phone', 'address', 'website', 'contact_person')
        }),
        ('Curriculum & Settings', {
            'fields': ('curriculum', 'secondary_curriculum', 'timezone', 'currency')
        }),
        ('School Levels', {
            'fields': ('has_baby_care', 'has_nursery', 'has_pre_primary', 'has_primary', 'has_olevel', 'has_alevel', 'has_secondary', 'has_technical', 'has_vocational', 'has_tertiary', 'has_teachers_college', 'has_business_college', 'has_health_college', 'has_university')
        }),
        ('Subscription', {
            'fields': ('is_active', 'subscription_start', 'subscription_end', 'max_students', 'max_staff')
        }),
        ('Payment Tracking', {
            'fields': ('last_payment_date', 'next_payment_due_date', 'is_access_blocked', 'payment_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Department)
class DepartmentAdmin(SchoolFilteredAdmin):
    list_display = ['name', 'school', 'head', 'is_active']
    list_filter = ['school', 'is_active']
    search_fields = ['name', 'school__name']


@admin.register(AcademicYear)
class AcademicYearAdmin(SchoolFilteredAdmin):
    list_display = ['name', 'school', 'start_date', 'end_date', 'is_current']
    list_filter = ['school', 'is_current']
    search_fields = ['name', 'school__name']


@admin.register(Grade)
class GradeAdmin(SchoolFilteredAdmin):
    list_display = ['name', 'school', 'level', 'capacity']
    list_filter = ['school', 'level']
    search_fields = ['name', 'school__name']


@admin.register(Student)
class StudentAdmin(SchoolFilteredAdmin):
    list_display = ['admission_number', 'get_full_name', 'school', 'grade', 'status', 'guardian_phone']
    list_filter = ['school', 'status', 'grade', 'scholarship_status', 'gender']
    search_fields = ['admission_number', 'first_name', 'last_name', 'school__name', 'guardian_name', 'guardian_phone']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('school', 'admission_number', 'first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender', 'photo')
        }),
        ('Academic Information', {
            'fields': ('grade', 'admission_date', 'status', 'scholarship_status', 'scholarship_percentage', 'scholarship_remarks')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Primary Guardian', {
            'fields': ('guardian_name', 'guardian_relationship', 'guardian_phone', 'guardian_email', 'guardian_address', 'guardian_occupation', 'guardian_workplace')
        }),
        ('Secondary Parent/Guardian', {
            'fields': ('parent2_name', 'parent2_relationship', 'parent2_phone', 'parent2_email', 'parent2_occupation', 'parent2_workplace')
        }),
        ('Emergency Contacts', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact2_name', 'emergency_contact2_phone', 'emergency_contact2_relationship')
        }),
        ('Medical Information', {
            'fields': ('blood_group', 'allergies', 'medical_conditions')
        }),
        ('Documents', {
            'fields': ('birth_certificate', 'previous_report_card', 'transfer_certificate', 'other_documents')
        }),
    )


@admin.register(GatePass)
class GatePassAdmin(SchoolFilteredAdmin):
    list_display = ['pass_number', 'student', 'exit_date', 'status', 'approved_by']
    list_filter = ['school', 'status', 'reason', 'exit_date']
    search_fields = ['pass_number', 'student__first_name', 'student__last_name', 'parent_name']
    readonly_fields = ['pass_number', 'created_at', 'updated_at']


@admin.register(Expense)
class ExpenseAdmin(SchoolFilteredAdmin):
    list_display = ['expense_number', 'vendor_name', 'amount', 'expense_type', 'is_approved', 'is_paid', 'paid_by']
    list_filter = ['school', 'expense_type', 'is_approved', 'is_paid', 'is_verified', 'expense_date']
    search_fields = ['expense_number', 'vendor_name', 'description']
    readonly_fields = ['expense_number', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('school', 'expense_number', 'expense_type', 'category', 'description')
        }),
        ('Financial Details', {
            'fields': ('amount', 'currency', 'payment_method', 'payment_reference', 'bank_account')
        }),
        ('Vendor Information', {
            'fields': ('vendor_name', 'vendor_phone', 'vendor_email', 'vendor_tin')
        }),
        ('Dates', {
            'fields': ('expense_date', 'payment_date')
        }),
        ('Approval & Payment', {
            'fields': ('requested_by', 'approved_by', 'approved_at', 'paid_by', 'paid_at', 'is_approved', 'is_paid', 'is_verified')
        }),
        ('Documentation', {
            'fields': ('receipt_image', 'invoice_image', 'supporting_documents', 'notes')
        }),
    )


@admin.register(Budget)
class BudgetAdmin(SchoolFilteredAdmin):
    list_display = ['budget_number', 'title', 'budget_type', 'total_budget', 'total_spent', 'status']
    list_filter = ['school', 'budget_type', 'status', 'start_date']
    search_fields = ['budget_number', 'title']
    readonly_fields = ['budget_number', 'created_at', 'updated_at']


@admin.register(BudgetLine)
class BudgetLineAdmin(admin.ModelAdmin):
    list_display = ['budget', 'category', 'subcategory', 'allocated_amount', 'spent_amount', 'priority']
    list_filter = ['budget__school', 'category', 'priority', 'is_essential']
    search_fields = ['category', 'subcategory', 'description']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            user_school = request.user.userprofile.school
            return qs.filter(budget__school=user_school)
        except:
            return qs.none()


@admin.register(Visitor)
class VisitorAdmin(SchoolFilteredAdmin):
    list_display = ['visitor_number', 'full_name', 'visitor_type', 'visit_date', 'is_checked_out']
    list_filter = ['school', 'visitor_type', 'purpose', 'visit_date', 'is_checked_out']
    search_fields = ['visitor_number', 'full_name', 'phone', 'company']
    readonly_fields = ['visitor_number', 'created_at', 'updated_at']


@admin.register(WorkshopExpense)
class WorkshopExpenseAdmin(SchoolFilteredAdmin):
    list_display = ['workshop_number', 'title', 'start_date', 'facilitator_name', 'total_cost', 'is_completed']
    list_filter = ['school', 'start_date', 'is_completed']
    search_fields = ['workshop_number', 'title', 'facilitator_name']
    readonly_fields = ['workshop_number', 'created_at', 'updated_at']
    
    def total_cost(self, obj):
        return f"UGX {obj.total_cost:,.0f}"
    total_cost.short_description = 'Total Cost'
