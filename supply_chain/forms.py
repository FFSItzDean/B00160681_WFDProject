from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    User, Restaurant, Supplier, Product, PurchaseOrder, 
    OrderItem, Invoice, InvoiceItem, Payment, Delivery, SupportCase, CaseResponse
)

# User registration form
class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'phone', 'password1', 'password2']

# Purchase Order form
class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'delivery_date', 'notes']
        widgets = {
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

# Order Item form
class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'unit_price']
    
    def __init__(self, *args, **kwargs):
        supplier = kwargs.pop('supplier', None)
        super().__init__(*args, **kwargs)
        if supplier:
            self.fields['product'].queryset = Product.objects.filter(supplier=supplier)

# Invoice form
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['purchase_order', 'due_date', 'tax_rate', 'discount', 'notes']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

# Invoice Item form
class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product', 'description', 'quantity', 'unit_price']

# Payment form
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_date', 'payment_method', 'reference_number', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

# Delivery form
class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['driver', 'scheduled_date', 'notes']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

# Support Case form
class SupportCaseForm(forms.ModelForm):
    class Meta:
        model = SupportCase
        fields = ['subject', 'description', 'priority']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

# Case Response form
class CaseResponseForm(forms.ModelForm):
    class Meta:
        model = CaseResponse
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }

# Product form
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'unit_price', 'unit', 'stock_quantity', 'reorder_level']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
