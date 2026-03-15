from django.contrib import admin
from .models import (
    AssetCategory, Asset, SupplyCategory, Supply, 
    Purchase, PurchaseItem, StockMovement, LowStockAlert
)


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_number', 'name', 'category', 'status', 'condition', 'purchase_price', 'current_value', 'location']
    list_filter = ['status', 'condition', 'category', 'purchase_date']
    search_fields = ['asset_number', 'name', 'serial_number', 'model_number']
    date_hierarchy = 'purchase_date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Asset Information', {
            'fields': ('asset_number', 'name', 'category', 'description')
        }),
        ('Purchase Details', {
            'fields': ('purchase_date', 'purchase_price', 'supplier', 'invoice_number')
        }),
        ('Current Status', {
            'fields': ('status', 'condition', 'location', 'assigned_to')
        }),
        ('Maintenance', {
            'fields': ('last_maintenance_date', 'next_maintenance_date', 'warranty_expiry_date')
        }),
        ('Depreciation', {
            'fields': ('depreciation_rate', 'current_value')
        }),
        ('Additional Info', {
            'fields': ('serial_number', 'model_number', 'manufacturer', 'notes')
        }),
    )
    
    actions = ['calculate_depreciation']
    
    def calculate_depreciation(self, request, queryset):
        for asset in queryset:
            asset.calculate_current_value()
            asset.save()
        self.message_user(request, f'Depreciation calculated for {queryset.count()} assets.')
    calculate_depreciation.short_description = 'Calculate current value (depreciation)'


@admin.register(SupplyCategory)
class SupplyCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ['item_code', 'name', 'category', 'current_stock', 'minimum_stock', 'unit', 'unit_price', 'is_low_stock']
    list_filter = ['category', 'unit']
    search_fields = ['item_code', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Supply Information', {
            'fields': ('item_code', 'name', 'category', 'description')
        }),
        ('Stock Management', {
            'fields': ('unit', 'current_stock', 'minimum_stock', 'maximum_stock')
        }),
        ('Pricing & Location', {
            'fields': ('unit_price', 'storage_location')
        }),
    )
    
    def is_low_stock(self, obj):
        return obj.is_low_stock()
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock'
    
    actions = ['check_low_stock']
    
    def check_low_stock(self, request, queryset):
        low_stock_items = []
        for supply in queryset:
            if supply.is_low_stock():
                low_stock_items.append(supply.name)
                # Create alert
                LowStockAlert.objects.get_or_create(
                    supply=supply,
                    status='active',
                    defaults={
                        'current_stock': supply.current_stock,
                        'minimum_stock': supply.minimum_stock
                    }
                )
        if low_stock_items:
            self.message_user(request, f'Low stock alerts created for: {", ".join(low_stock_items)}')
        else:
            self.message_user(request, 'No low stock items found.')
    check_low_stock.short_description = 'Check and create low stock alerts'


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    fields = ['supply', 'quantity', 'unit_price', 'total_price', 'quantity_received']
    readonly_fields = ['total_price']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['purchase_order_number', 'supplier', 'purchase_date', 'status', 'final_amount', 'is_paid']
    list_filter = ['status', 'is_paid', 'purchase_date']
    search_fields = ['purchase_order_number', 'supplier', 'payment_reference']
    date_hierarchy = 'purchase_date'
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PurchaseItemInline]
    
    fieldsets = (
        ('Purchase Information', {
            'fields': ('purchase_order_number', 'purchase_date', 'supplier', 'supplier_contact')
        }),
        ('Financial', {
            'fields': ('total_amount', 'tax_amount', 'discount_amount', 'final_amount')
        }),
        ('Status', {
            'fields': ('status', 'expected_delivery_date', 'actual_delivery_date')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_reference', 'is_paid', 'payment_date')
        }),
        ('Staff', {
            'fields': ('requested_by', 'approved_by', 'received_by')
        }),
        ('Additional', {
            'fields': ('notes', 'invoice_file')
        }),
    )
    
    actions = ['mark_as_received', 'calculate_totals']
    
    def mark_as_received(self, request, queryset):
        from datetime import date
        queryset.update(status='received', actual_delivery_date=date.today())
        self.message_user(request, f'{queryset.count()} purchases marked as received.')
    mark_as_received.short_description = 'Mark as received'
    
    def calculate_totals(self, request, queryset):
        for purchase in queryset:
            purchase.calculate_final_amount()
            purchase.save()
        self.message_user(request, f'Totals calculated for {queryset.count()} purchases.')
    calculate_totals.short_description = 'Calculate final amounts'


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['supply', 'movement_type', 'quantity', 'previous_stock', 'new_stock', 'moved_by', 'movement_date']
    list_filter = ['movement_type', 'movement_date']
    search_fields = ['supply__name', 'reference_number', 'reason']
    date_hierarchy = 'movement_date'
    readonly_fields = ['movement_date']


@admin.register(LowStockAlert)
class LowStockAlertAdmin(admin.ModelAdmin):
    list_display = ['supply', 'current_stock', 'minimum_stock', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['supply__name']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    actions = ['mark_acknowledged', 'mark_resolved']
    
    def mark_acknowledged(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='acknowledged', acknowledged_by=request.user, acknowledged_at=timezone.now())
        self.message_user(request, f'{queryset.count()} alerts marked as acknowledged.')
    mark_acknowledged.short_description = 'Mark as acknowledged'
    
    def mark_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f'{queryset.count()} alerts marked as resolved.')
    mark_resolved.short_description = 'Mark as resolved'
