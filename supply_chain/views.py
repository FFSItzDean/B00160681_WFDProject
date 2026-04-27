from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    User, Restaurant, Supplier, Category, Product, 
    PurchaseOrder, OrderItem, Invoice, InvoiceItem, 
    Payment, Delivery, DeliveryItem, SupportCase, CaseResponse
)
from .forms import (
    UserRegistrationForm, PurchaseOrderForm, OrderItemForm,
    InvoiceForm, InvoiceItemForm, PaymentForm, DeliveryForm,
    SupportCaseForm, CaseResponseForm, ProductForm
)

# Authentication views
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard view
@login_required
def dashboard(request):
    context = {'user': request.user}
    
    # Role-specific dashboard data
    if request.user.role == 'MANAGER':
        restaurant = Restaurant.objects.filter(manager=request.user).first()
        if restaurant:
            context['restaurant'] = restaurant
            context['pending_orders'] = PurchaseOrder.objects.filter(restaurant=restaurant, status='SUBMITTED').count()
            context['pending_invoices'] = Invoice.objects.filter(restaurant=restaurant, status='PENDING').count()
            context['open_cases'] = SupportCase.objects.filter(restaurant=restaurant, status='OPEN').count()
    
    elif request.user.role == 'SUPPLIER':
        supplier = Supplier.objects.filter(contact_person=request.user).first()
        if supplier:
            context['supplier'] = supplier
            context['new_orders'] = PurchaseOrder.objects.filter(supplier=supplier, status='SUBMITTED').count()
            context['pending_invoices'] = Invoice.objects.filter(supplier=supplier, status='PENDING').count()
    
    elif request.user.role == 'WAREHOUSE':
        context['pending_deliveries'] = Delivery.objects.filter(status='PENDING').count()
        context['low_stock_items'] = Product.objects.filter(stock_quantity__lte=F('reorder_level')).count()
    
    elif request.user.role == 'DRIVER':
        context['assigned_deliveries'] = Delivery.objects.filter(driver=request.user, status__in=['PENDING', 'IN_TRANSIT']).count()
    
    elif request.user.role == 'ACCOUNTANT':
        context['pending_invoices'] = Invoice.objects.filter(status='PENDING').count()
        context['overdue_invoices'] = Invoice.objects.filter(status='OVERDUE').count()
    
    return render(request, 'dashboard.html', context)

# Purchase Order views
@login_required
def purchase_order_list(request):
    if request.user.role == 'MANAGER':
        restaurant = Restaurant.objects.filter(manager=request.user).first()
        orders = PurchaseOrder.objects.filter(restaurant=restaurant).order_by('-order_date')
    elif request.user.role == 'SUPPLIER':
        supplier = Supplier.objects.filter(contact_person=request.user).first()
        orders = PurchaseOrder.objects.filter(supplier=supplier).order_by('-order_date')
    else:
        orders = PurchaseOrder.objects.all().order_by('-order_date')
    
    return render(request, 'purchase_orders/list.html', {'orders': orders})

@login_required
def purchase_order_create(request):
    restaurant = Restaurant.objects.filter(manager=request.user).first()
    if not restaurant:
        messages.error(request, 'You must be assigned to a restaurant')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.restaurant = restaurant
            order.created_by = request.user
            # Generate order number
            order.order_number = f"{datetime.now().strftime('%Y%m%d')}{PurchaseOrder.objects.count() + 1:04d}"
            order.save()
            messages.success(request, 'Purchase order created successfully')
            return redirect('purchase_order_detail', pk=order.pk)
    else:
        form = PurchaseOrderForm()
    
    return render(request, 'purchase_orders/create.html', {'form': form})

@login_required
def purchase_order_detail(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    return render(request, 'purchase_orders/detail.html', {'order': order})

@login_required
def purchase_order_add_item(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    
    if request.method == 'POST':
        form = OrderItemForm(request.POST, supplier=order.supplier)
        if form.is_valid():
            item = form.save(commit=False)
            item.purchase_order = order
            item.save()
            messages.success(request, 'Item added to order')
            return redirect('purchase_order_detail', pk=order.pk)
    else:
        form = OrderItemForm(supplier=order.supplier)
    
    return render(request, 'purchase_orders/add_item.html', {'form': form, 'order': order})

@login_required
def purchase_order_submit(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if order.items.count() == 0:
        messages.error(request, 'Cannot submit empty order')
    else:
        order.status = 'SUBMITTED'
        order.save()
        messages.success(request, 'Order submitted successfully')
    return redirect('purchase_order_detail', pk=order.pk)

@login_required
def purchase_order_approve(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    order.status = 'APPROVED'
    order.save()
    messages.success(request, 'Order approved')
    return redirect('purchase_order_detail', pk=order.pk)

# Invoice views (MUST-HAVE USE CASE)
@login_required
def invoice_list(request):
    if request.user.role == 'MANAGER':
        restaurant = Restaurant.objects.filter(manager=request.user).first()
        invoices = Invoice.objects.filter(restaurant=restaurant).order_by('-issue_date')
    elif request.user.role == 'SUPPLIER':
        supplier = Supplier.objects.filter(contact_person=request.user).first()
        invoices = Invoice.objects.filter(supplier=supplier).order_by('-issue_date')
    else:
        invoices = Invoice.objects.all().order_by('-issue_date')
    
    return render(request, 'invoices/list.html', {'invoices': invoices})

@login_required
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            po = invoice.purchase_order
            invoice.restaurant = po.restaurant
            invoice.supplier = po.supplier
            # Generate invoice number
            invoice.invoice_number = f"INV{datetime.now().strftime('%Y%m%d')}{Invoice.objects.count() + 1:04d}"
            invoice.save()
            
            # Copy items from purchase order
            for order_item in po.items.all():
                InvoiceItem.objects.create(
                    invoice=invoice,
                    product=order_item.product,
                    description=order_item.product.name,
                    quantity=order_item.quantity,
                    unit_price=order_item.unit_price
                )
            
            # Calculate subtotal
            invoice.subtotal = sum(item.subtotal for item in invoice.items.all())
            invoice.save()
            
            messages.success(request, 'Invoice created successfully')
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
    
    return render(request, 'invoices/create.html', {'form': form})

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    payments = Payment.objects.filter(invoice=invoice)
    total_paid = sum(p.amount for p in payments)
    balance = invoice.total_amount - total_paid
    
    context = {
        'invoice': invoice,
        'payments': payments,
        'total_paid': total_paid,
        'balance': balance,
    }
    return render(request, 'invoices/detail.html', context)

@login_required
def invoice_add_item(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.method == 'POST':
        form = InvoiceItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.invoice = invoice
            item.save()
            
            # Recalculate subtotal
            invoice.subtotal = sum(i.subtotal for i in invoice.items.all())
            invoice.save()
            
            messages.success(request, 'Item added to invoice')
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceItemForm()
    
    return render(request, 'invoices/add_item.html', {'form': form, 'invoice': invoice})

# Payment views
@login_required
def payment_create(request, invoice_pk):
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.processed_by = request.user
            payment.save()
            
            # Update invoice status
            total_paid = sum(p.amount for p in invoice.payments.all())
            if total_paid >= invoice.total_amount:
                invoice.status = 'PAID'
                invoice.save()
            
            messages.success(request, 'Payment recorded successfully')
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = PaymentForm()
    
    return render(request, 'payments/create.html', {'form': form, 'invoice': invoice})

# Product/Inventory views
@login_required
def product_list(request):
    products = Product.objects.all().select_related('category', 'supplier')
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Filter by supplier
    supplier_id = request.GET.get('supplier')
    if supplier_id:
        products = products.filter(supplier_id=supplier_id)
    
    # Show only low stock
    if request.GET.get('low_stock'):
        products = products.filter(stock_quantity__lte=models.F('reorder_level'))
    
    categories = Category.objects.all()
    suppliers = Supplier.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'suppliers': suppliers,
    }
    return render(request, 'products/list.html', context)

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/detail.html', {'product': product})

# Delivery views
@login_required
def delivery_list(request):
    if request.user.role == 'DRIVER':
        deliveries = Delivery.objects.filter(driver=request.user).order_by('-scheduled_date')
    else:
        deliveries = Delivery.objects.all().order_by('-scheduled_date')
    
    return render(request, 'deliveries/list.html', {'deliveries': deliveries})

@login_required
def delivery_create(request, po_pk):
    purchase_order = get_object_or_404(PurchaseOrder, pk=po_pk)
    
    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        if form.is_valid():
            delivery = form.save(commit=False)
            delivery.purchase_order = purchase_order
            # Generate delivery number
            delivery.delivery_number = f"DEL{datetime.now().strftime('%Y%m%d')}{Delivery.objects.count() + 1:04d}"
            delivery.save()
            
            # Copy items from purchase order
            for order_item in purchase_order.items.all():
                DeliveryItem.objects.create(
                    delivery=delivery,
                    product=order_item.product,
                    quantity=order_item.quantity
                )
            
            messages.success(request, 'Delivery scheduled successfully')
            return redirect('delivery_detail', pk=delivery.pk)
    else:
        form = DeliveryForm()
    
    return render(request, 'deliveries/create.html', {'form': form, 'purchase_order': purchase_order})

@login_required
def delivery_detail(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    return render(request, 'deliveries/detail.html', {'delivery': delivery})

@login_required
def delivery_update_status(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    new_status = request.POST.get('status')
    
    if new_status in dict(Delivery.STATUS_CHOICES):
        delivery.status = new_status
        if new_status == 'DELIVERED':
            delivery.actual_delivery_date = timezone.now()
        delivery.save()
        messages.success(request, f'Delivery status updated to {delivery.get_status_display()}')
    
    return redirect('delivery_detail', pk=delivery.pk)

# Support Case views
@login_required
def support_case_list(request):
    if request.user.role == 'MANAGER':
        restaurant = Restaurant.objects.filter(manager=request.user).first()
        cases = SupportCase.objects.filter(restaurant=restaurant).order_by('-created_at')
    else:
        cases = SupportCase.objects.all().order_by('-created_at')
    
    return render(request, 'support/list.html', {'cases': cases})

@login_required
def support_case_create(request):
    restaurant = Restaurant.objects.filter(manager=request.user).first()
    if not restaurant:
        messages.error(request, 'You must be assigned to a restaurant')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SupportCaseForm(request.POST)
        if form.is_valid():
            case = form.save(commit=False)
            case.restaurant = restaurant
            case.created_by = request.user
            # Generate case number
            case.case_number = f"CASE{datetime.now().strftime('%Y%m%d')}{SupportCase.objects.count() + 1:04d}"
            case.save()
            messages.success(request, 'Support case created successfully')
            return redirect('support_case_detail', pk=case.pk)
    else:
        form = SupportCaseForm()
    
    return render(request, 'support/create.html', {'form': form})

@login_required
def support_case_detail(request, pk):
    case = get_object_or_404(SupportCase, pk=pk)
    
    if request.method == 'POST':
        form = CaseResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.case = case
            response.user = request.user
            response.save()
            
            # Update case status
            if case.status == 'OPEN':
                case.status = 'IN_PROGRESS'
                case.save()
            
            messages.success(request, 'Response added')
            return redirect('support_case_detail', pk=case.pk)
    else:
        form = CaseResponseForm()
    
    return render(request, 'support/detail.html', {'case': case, 'form': form})

@login_required
def support_case_resolve(request, pk):
    case = get_object_or_404(SupportCase, pk=pk)
    case.status = 'RESOLVED'
    case.resolved_at = timezone.now()
    case.save()
    messages.success(request, 'Case marked as resolved')
    return redirect('support_case_detail', pk=case.pk)

# Analytics/Reports view
@login_required
def reports_view(request):
    context = {}
    
    # Sales analytics
    if request.user.role in ['ADMIN', 'ACCOUNTANT', 'SUPPLIER']:
        # Total sales by month
        invoices = Invoice.objects.filter(status='PAID')
        context['total_revenue'] = sum(inv.total_amount for inv in invoices)
        context['total_invoices'] = invoices.count()
        
        # Top products
        top_products = Product.objects.annotate(
            total_sold=Sum('orderitem__quantity')
        ).order_by('-total_sold')[:10]
        context['top_products'] = top_products
    
    return render(request, 'reports/analytics.html', context)
