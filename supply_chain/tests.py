from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta
from .models import (
    Restaurant, Supplier, Category, Product, 
    PurchaseOrder, OrderItem, Invoice, InvoiceItem,
    Payment, Delivery, DeliveryItem, SupportCase, CaseResponse
)

User = get_user_model()

class UserModelTest(TestCase):
    """Test User model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='password',
            role='MANAGER'
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.role, 'MANAGER')
        self.assertTrue(self.user.check_password('password'))
    


class RestaurantModelTest(TestCase):
    """Test Restaurant model"""
    
    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager',
            password='password',
            role='MANAGER'
        )
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            address='123 Test St',
            phone='123-456-7890',
            email='test@restaurant.com',
            manager=self.manager
        )
    
    def test_restaurant_creation(self):
        self.assertEqual(self.restaurant.name, 'Test Restaurant')
        self.assertEqual(self.restaurant.manager, self.manager)


class ProductModelTest(TestCase):
    """Test Product model"""
    
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            address='Test Address',
            phone='123-456-7890',
            email='supplier@test.com'
        )
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            supplier=self.supplier,
            unit_price=Decimal('10.00'),
            stock_quantity=100,
            reorder_level=20
        )
    
    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.unit_price, Decimal('10.00'))


class PurchaseOrderModelTest(TestCase):
    """Test PurchaseOrder model"""
    
    def setUp(self):
        self.manager = User.objects.create_user(username='manager', password='password', role='MANAGER')
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            address='Test Address',
            phone='123-456-7890',
            email='test@restaurant.com',
            manager=self.manager
        )
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            address='Test Address',
            phone='123-456-7890',
            email='supplier@test.com'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            supplier=self.supplier,
            unit_price=Decimal('10.00'),
            stock_quantity=100,
            reorder_level=20
        )
        self.order = PurchaseOrder.objects.create(
            order_number='PO001',
            restaurant=self.restaurant,
            supplier=self.supplier,
            status='DRAFT',
            created_by=self.manager
        )
        self.order_item = OrderItem.objects.create(
            purchase_order=self.order,
            product=self.product,
            quantity=10,
            unit_price=Decimal('10.00')
        )
    
    def test_purchase_order_creation(self):
        self.assertEqual(self.order.order_number, 'PO001')
        self.assertEqual(self.order.status, 'DRAFT')
        self.assertEqual(self.order.total_amount, Decimal('100.00'))


class InvoiceModelTest(TestCase):
    """Test Invoice model (MUST-HAVE USE CASE)"""
    
    def setUp(self):
        self.manager = User.objects.create_user(username='manager', password='password', role='MANAGER')
        self.supplier_user = User.objects.create_user(username='supplier', password='password', role='SUPPLIER')
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            address='Test Address',
            phone='123-456-7890',
            email='test@restaurant.com',
            manager=self.manager
        )
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            address='Test Address',
            phone='123-456-7890',
            email='supplier@test.com',
            contact_person=self.supplier_user
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            supplier=self.supplier,
            unit_price=Decimal('10.00'),
            stock_quantity=100,
            reorder_level=20
        )
        self.order = PurchaseOrder.objects.create(
            order_number='PO001',
            restaurant=self.restaurant,
            supplier=self.supplier,
            status='APPROVED',
            created_by=self.manager
        )
        self.invoice = Invoice.objects.create(
            invoice_number='INV001',
            purchase_order=self.order,
            restaurant=self.restaurant,
            supplier=self.supplier,
            due_date=date.today() + timedelta(days=30),
            subtotal=Decimal('100.00'),
            tax_rate=Decimal('13.5'),
            discount=Decimal('0.00'),
            created_by=self.supplier_user
        )
        self.invoice_item = InvoiceItem.objects.create(
            invoice=self.invoice,
            product=self.product,
            description='Test Product',
            quantity=10,
            unit_price=Decimal('10.00')
        )
    
    def test_invoice_creation_and_calculations(self):
        self.assertEqual(self.invoice.invoice_number, 'INV001')
        self.assertEqual(self.invoice.status, 'PENDING')
        self.assertEqual(self.invoice_item.subtotal, Decimal('100.00'))
        self.assertEqual(self.invoice.total_amount, Decimal('113.50'))


class AuthenticationTest(TestCase):
    """Test authentication views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='password',
            role='MANAGER'
        )
    
    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')
    
    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password'
        })
        self.assertRedirects(response, reverse('dashboard'))
    
    def test_logout(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))


class DashboardTest(TestCase):
    """Test dashboard view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='password',
            role='MANAGER'
        )
    
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/?next=/dashboard/')
    
    def test_dashboard_authenticated(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')


class InvoiceViewTest(TestCase):
    """Test invoice views (MUST-HAVE USE CASE)"""
    
    def setUp(self):
        self.client = Client()
        self.supplier_user = User.objects.create_user(username='supplier', password='password', role='SUPPLIER')
        self.manager = User.objects.create_user(username='manager', password='password', role='MANAGER')
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            address='Test Address',
            phone='123-456-7890',
            email='test@restaurant.com',
            manager=self.manager
        )
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            address='Test Address',
            phone='123-456-7890',
            email='supplier@test.com',
            contact_person=self.supplier_user
        )
        self.order = PurchaseOrder.objects.create(
            order_number='PO001',
            restaurant=self.restaurant,
            supplier=self.supplier,
            created_by=self.manager
        )
        self.client.login(username='supplier', password='password')
    
    def test_invoice_list_view(self):
        response = self.client.get(reverse('invoice_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoices/list.html')
    
    def test_invoice_create_view(self):
        response = self.client.get(reverse('invoice_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoices/create.html')


class IntegrationTest(TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        self.client = Client()
        self.manager = User.objects.create_user(username='manager', password='password', role='MANAGER')
        self.supplier_user = User.objects.create_user(username='supplier', password='password', role='SUPPLIER')
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            address='Test Address',
            phone='123-456-7890',
            email='test@restaurant.com',
            manager=self.manager
        )
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            address='Test Address',
            phone='123-456-7890',
            email='supplier@test.com',
            contact_person=self.supplier_user
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            supplier=self.supplier,
            unit_price=Decimal('10.00'),
            stock_quantity=100,
            reorder_level=20
        )
    
    def test_complete_order_to_invoice_workflow(self):
        # Manager creates purchase order
        self.client.login(username='manager', password='password')
        order = PurchaseOrder.objects.create(
            order_number='PO001',
            restaurant=self.restaurant,
            supplier=self.supplier,
            status='DRAFT',
            created_by=self.manager
        )
        
        # Add items to order
        OrderItem.objects.create(
            purchase_order=order,
            product=self.product,
            quantity=10,
            unit_price=Decimal('10.00')
        )
        
        # Submit order
        order.status = 'SUBMITTED'
        order.save()
        self.assertEqual(order.status, 'SUBMITTED')
        
        # Supplier creates invoice
        self.client.login(username='supplier', password='password')
        invoice = Invoice.objects.create(
            invoice_number='INV001',
            purchase_order=order,
            restaurant=self.restaurant,
            supplier=self.supplier,
            due_date=date.today() + timedelta(days=30),
            subtotal=Decimal('100.00'),
            tax_rate=Decimal('13.5'),
            created_by=self.supplier_user
        )
        
        # Verify invoice total
        self.assertEqual(invoice.total_amount, Decimal('113.50'))
        self.assertEqual(invoice.status, 'PENDING')
