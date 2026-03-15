from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class AssetCategory(models.Model):
    """
    Categories for school assets
    
    TENANT ISOLATION: Global categories (no school FK)
    Shared across all schools - not tenant-specific
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Asset Categories'
    
    def __str__(self):
        return self.name


class Asset(models.Model):
    """
    School assets and equipment
    
    TENANT ISOLATION: Global assets (no school FK)
    NOTE: Should add school FK in future for proper multi-tenant isolation
    Currently shared across schools - NOT RECOMMENDED for production
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('under_maintenance', 'Under Maintenance'),
        ('damaged', 'Damaged'),
        ('disposed', 'Disposed'),
        ('lost', 'Lost'),
    ]
    
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    # Asset Information
    asset_number = models.CharField(max_length=50, unique=True, help_text='Unique asset identification number')
    name = models.CharField(max_length=200)
    category = models.ForeignKey(AssetCategory, on_delete=models.SET_NULL, null=True, related_name='assets')
    description = models.TextField(blank=True)
    
    # Purchase Details
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    supplier = models.CharField(max_length=200, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True)
    
    # Current Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    location = models.CharField(max_length=200, help_text='Where the asset is located')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_assets', help_text='Staff member responsible')
    
    # Maintenance
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    warranty_expiry_date = models.DateField(null=True, blank=True)
    
    # Depreciation
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Annual depreciation rate (%)')
    current_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Additional Info
    serial_number = models.CharField(max_length=100, blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    
    # System fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_assets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['asset_number']
        indexes = [
            models.Index(fields=['asset_number']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.asset_number} - {self.name}"
    
    def calculate_current_value(self):
        """Calculate current value based on depreciation"""
        from datetime import date
        years = (date.today() - self.purchase_date).days / 365.25
        depreciation_amount = self.purchase_price * (self.depreciation_rate / 100) * Decimal(str(years))
        self.current_value = max(self.purchase_price - depreciation_amount, Decimal('0.00'))
        return self.current_value


class SupplyCategory(models.Model):
    """
    Categories for supplies
    
    TENANT ISOLATION: Global categories (no school FK)
    Shared across all schools - not tenant-specific
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Supply Categories'
    
    def __str__(self):
        return self.name


class Supply(models.Model):
    """
    School supplies and consumables
    
    TENANT ISOLATION: Global supplies (no school FK)
    NOTE: Should add school FK in future for proper multi-tenant isolation
    Currently shared across schools - NOT RECOMMENDED for production
    """
    UNIT_CHOICES = [
        ('piece', 'Piece'),
        ('box', 'Box'),
        ('pack', 'Pack'),
        ('ream', 'Ream'),
        ('dozen', 'Dozen'),
        ('kg', 'Kilogram'),
        ('liter', 'Liter'),
        ('meter', 'Meter'),
        ('set', 'Set'),
    ]
    
    # Supply Information
    item_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(SupplyCategory, on_delete=models.SET_NULL, null=True, related_name='supplies')
    description = models.TextField(blank=True)
    
    # Stock Management
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='piece')
    current_stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    minimum_stock = models.IntegerField(default=10, validators=[MinValueValidator(0)], help_text='Reorder level')
    maximum_stock = models.IntegerField(default=100, validators=[MinValueValidator(0)])
    
    # Pricing
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Location
    storage_location = models.CharField(max_length=200, blank=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Supplies'
        indexes = [
            models.Index(fields=['item_code']),
            models.Index(fields=['current_stock']),
        ]
    
    def __str__(self):
        return f"{self.item_code} - {self.name}"
    
    def is_low_stock(self):
        """Check if stock is below minimum level"""
        return self.current_stock <= self.minimum_stock
    
    def stock_value(self):
        """Calculate total value of current stock"""
        return self.current_stock * self.unit_price


class Purchase(models.Model):
    """
    Purchase records for supplies and assets
    
    TENANT ISOLATION: Global purchases (no school FK)
    NOTE: Should add school FK in future for proper multi-tenant isolation
    Currently shared across schools - NOT RECOMMENDED for production
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('ordered', 'Ordered'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Purchase Information
    purchase_order_number = models.CharField(max_length=50, unique=True)
    purchase_date = models.DateField()
    supplier = models.CharField(max_length=200)
    supplier_contact = models.CharField(max_length=100, blank=True)
    
    # Financial
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    # Payment
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    
    # Staff
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='requested_purchases')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_purchases')
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_purchases')
    
    # Notes
    notes = models.TextField(blank=True)
    invoice_file = models.FileField(upload_to='inventory/invoices/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-purchase_date']
        indexes = [
            models.Index(fields=['purchase_order_number']),
            models.Index(fields=['status']),
            models.Index(fields=['purchase_date']),
        ]
    
    def __str__(self):
        return f"{self.purchase_order_number} - {self.supplier}"
    
    def calculate_final_amount(self):
        """Calculate final amount after tax and discount"""
        self.final_amount = self.total_amount + self.tax_amount - self.discount_amount
        return self.final_amount


class PurchaseItem(models.Model):
    """Individual items in a purchase order"""
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    supply = models.ForeignKey(Supply, on_delete=models.CASCADE, related_name='purchase_items')
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    quantity_received = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['purchase', 'supply']
    
    def __str__(self):
        return f"{self.supply.name} - {self.quantity} {self.supply.unit}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate total price
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class StockMovement(models.Model):
    """Track stock movements (in/out)"""
    MOVEMENT_TYPE_CHOICES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
        ('damaged', 'Damaged'),
        ('expired', 'Expired'),
    ]
    
    supply = models.ForeignKey(Supply, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.IntegerField()
    
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    
    reason = models.TextField(help_text='Reason for stock movement')
    reference_number = models.CharField(max_length=100, blank=True, help_text='PO number, requisition number, etc.')
    
    moved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='stock_movements')
    movement_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-movement_date']
        indexes = [
            models.Index(fields=['supply', '-movement_date']),
            models.Index(fields=['movement_type']),
        ]
    
    def __str__(self):
        return f"{self.supply.name} - {self.movement_type} - {self.quantity}"


class LowStockAlert(models.Model):
    """Alerts for low stock items"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]
    
    supply = models.ForeignKey(Supply, on_delete=models.CASCADE, related_name='alerts')
    current_stock = models.IntegerField()
    minimum_stock = models.IntegerField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Low Stock Alert: {self.supply.name} ({self.current_stock}/{self.minimum_stock})"
