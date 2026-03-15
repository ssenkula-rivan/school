from django.contrib import admin
from .models import (
    UserProfile, AuditLog, LoginLog, SchoolConfiguration,
    Parent, ParentStudentLink, ParentTeacherMessage
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'role', 'department', 'is_active_employee']
    list_filter = ['role', 'is_active_employee', 'department']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'employee_id']


@admin.register(SchoolConfiguration)
class SchoolConfigurationAdmin(admin.ModelAdmin):
    list_display = ['school_name', 'school_type', 'institution_type', 'is_configured']
    list_filter = ['school_type', 'institution_type', 'is_configured']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'timestamp', 'ip_address']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'action', 'details']
    date_hierarchy = 'timestamp'


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'occupation', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone', 'national_id']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': ('phone', 'address', 'occupation', 'national_id')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(ParentStudentLink)
class ParentStudentLinkAdmin(admin.ModelAdmin):
    list_display = ['parent', 'student', 'relationship', 'is_primary_contact', 'can_pickup']
    list_filter = ['relationship', 'is_primary_contact', 'can_pickup']
    search_fields = ['parent__user__first_name', 'parent__user__last_name', 
                    'student__first_name', 'student__last_name']
    
    fieldsets = (
        ('Link Information', {
            'fields': ('parent', 'student', 'relationship')
        }),
        ('Permissions', {
            'fields': ('is_primary_contact', 'can_pickup')
        }),
    )


@admin.register(ParentTeacherMessage)
class ParentTeacherMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'student', 'subject', 'status', 'sent_at']
    list_filter = ['sender_type', 'recipient_type', 'status', 'sent_at']
    search_fields = ['sender__username', 'recipient__username', 'student__first_name', 
                    'student__last_name', 'subject', 'message']
    date_hierarchy = 'sent_at'
    readonly_fields = ['sent_at', 'read_at']
    
    fieldsets = (
        ('Message Details', {
            'fields': ('sender_type', 'sender', 'recipient_type', 'recipient', 'student')
        }),
        ('Content', {
            'fields': ('subject', 'message', 'parent_message')
        }),
        ('Status', {
            'fields': ('status', 'sent_at', 'read_at')
        }),
    )
    
    actions = ['mark_as_read']
    
    def mark_as_read(self, request, queryset):
        for message in queryset:
            message.mark_as_read()
        self.message_user(request, f'{queryset.count()} messages marked as read.')
    mark_as_read.short_description = 'Mark selected messages as read'
