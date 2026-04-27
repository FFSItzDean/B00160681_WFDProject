from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Restaurant, Supplier, Category, Product, 
    PurchaseOrder, OrderItem, Invoice, InvoiceItem, 
    Payment, Delivery, DeliveryItem, SupportCase, CaseResponse
)

# Custom User admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone')}),
    )

# Inline admin classes
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

class DeliveryItemInline(admin.TabularInline):
    model = DeliveryItem
    extra = 1

class CaseResponseInline(admin.TabularInline):
    model = CaseResponse
    extra = 1

# Register models
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'manager']
    search_fields = ['name', 'email']

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'contact_person']
    search_fields = ['name', 'email']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'supplier', 'unit_price', 'stock_quantity', 'needs_reorder']
    list_filter = ['category', 'supplier']
    search_fields = ['name']

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'restaurant', 'supplier', 'status', 'order_date']
    list_filter = ['status', 'order_date']
    search_fields = ['order_number']
    inlines = [OrderItemInline]

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'restaurant', 'supplier', 'status', 'issue_date', 'due_date', 'total_amount']
    list_filter = ['status', 'issue_date']
    search_fields = ['invoice_number']
    inlines = [InvoiceItemInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'amount', 'payment_date', 'payment_method', 'processed_by']
    list_filter = ['payment_method', 'payment_date']

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['delivery_number', 'purchase_order', 'driver', 'status', 'scheduled_date']
    list_filter = ['status', 'scheduled_date']
    search_fields = ['delivery_number']
    inlines = [DeliveryItemInline]

@admin.register(SupportCase)
class SupportCaseAdmin(admin.ModelAdmin):
    list_display = ['case_number', 'restaurant', 'subject', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['case_number', 'subject']
    inlines = [CaseResponseInline]
