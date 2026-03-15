from django.contrib import admin
from .models import Plan, Subscription, SubscriptionInvoice


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'billing_cycle', 'max_students', 'max_teachers', 'is_active', 'is_public']
    list_filter = ['billing_cycle', 'is_active', 'is_public']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'description', 'sort_order')
        }),
        ('Pricing', {
            'fields': ('price', 'billing_cycle')
        }),
        ('Limits', {
            'fields': ('max_students', 'max_teachers', 'max_staff', 'max_storage_gb')
        }),
        ('Features', {
            'fields': ('feature_flags',)
        }),
        ('Trial & Status', {
            'fields': ('trial_days', 'is_active', 'is_public')
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['school', 'plan', 'status', 'current_period_end', 'is_active', 'days_until_expiry']
    list_filter = ['status', 'plan']
    search_fields = ['school__name', 'school__code', 'external_payment_id']
    readonly_fields = ['created_at', 'updated_at', 'is_active', 'is_trial', 'days_until_expiry']
    date_hierarchy = 'current_period_end'
    
    fieldsets = (
        ('Subscription', {
            'fields': ('school', 'plan', 'status')
        }),
        ('Billing Period', {
            'fields': ('current_period_start', 'current_period_end')
        }),
        ('Trial', {
            'fields': ('trial_start', 'trial_end')
        }),
        ('Payment Gateway', {
            'fields': ('external_payment_id', 'external_customer_id')
        }),
        ('Cancellation', {
            'fields': ('cancelled_at', 'cancel_reason', 'cancel_at_period_end')
        }),
        ('Status', {
            'fields': ('is_active', 'is_trial', 'days_until_expiry', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['suspend_subscriptions', 'activate_subscriptions']
    
    def suspend_subscriptions(self, request, queryset):
        count = 0
        for subscription in queryset:
            subscription.suspend(reason='Suspended by admin')
            count += 1
        self.message_user(request, f"{count} subscriptions suspended")
    suspend_subscriptions.short_description = "Suspend selected subscriptions"
    
    def activate_subscriptions(self, request, queryset):
        count = queryset.update(status='active')
        self.message_user(request, f"{count} subscriptions activated")
    activate_subscriptions.short_description = "Activate selected subscriptions"


@admin.register(SubscriptionInvoice)
class SubscriptionInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'subscription', 'amount', 'status', 'issue_date', 'due_date', 'paid_date']
    list_filter = ['status', 'issue_date']
    search_fields = ['invoice_number', 'subscription__school__name', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'issue_date'
    
    fieldsets = (
        ('Invoice', {
            'fields': ('subscription', 'invoice_number', 'amount', 'currency', 'status')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date', 'paid_date')
        }),
        ('Payment', {
            'fields': ('external_invoice_id', 'payment_method', 'transaction_id')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at')
        }),
    )
