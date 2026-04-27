"""
Script to load all fixture data
Run this after creating users: python load_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from supply_chain.models import (
    Restaurant, Supplier, Category, Product, 
    PurchaseOrder, OrderItem, Invoice, InvoiceItem,
    Payment, Delivery, DeliveryItem, SupportCase, CaseResponse, User
)
from datetime import datetime, timedelta
from decimal import Decimal

def load_data():
    """Load demo data into database"""
    
    # Get users
    admin = User.objects.get(username='admin')
    supplier1 = User.objects.get(username='supplier1')
    manager1 = User.objects.get(username='manager1')
    warehouse1 = User.objects.get(username='warehouse1')
    driver1 = User.objects.get(username='driver1')
    accountant1 = User.objects.get(username='accountant1')
    
    # Create categories
    print("Creating categories...")
    categories = {
        'produce': Category.objects.create(name='Produce', description='Fresh fruits and vegetables'),
        'dairy': Category.objects.create(name='Dairy', description='Milk, cheese, butter, and dairy products'),
        'meat': Category.objects.create(name='Meat & Poultry', description='Fresh and frozen meats'),
        'seafood': Category.objects.create(name='Seafood', description='Fresh and frozen seafood'),
        'dry': Category.objects.create(name='Dry Goods', description='Pasta, rice, flour, and dry ingredients'),
        'beverages': Category.objects.create(name='Beverages', description='Drinks and beverages'),
    }
    
    # Create restaurants
    print("Creating restaurants...")
    restaurant1 = Restaurant.objects.create(
        name='The Golden Fork',
        address='123 Main Street, Dublin, Ireland',
        phone='01-234-5678',
        email='info@goldenfork.ie',
        manager=manager1
    )
    
    # Create suppliers
    print("Creating suppliers...")
    supplier_fresh = Supplier.objects.create(
        name='Fresh Foods Ltd',
        address='789 Industrial Park, Dublin, Ireland',
        phone='01-987-6543',
        email='sales@freshfoods.ie',
        contact_person=supplier1
    )
    
    supplier_meat = Supplier.objects.create(
        name='Quality Meats Co',
        address='321 Business Center, Galway, Ireland',
        phone='091-234-5678',
        email='orders@qualitymeats.ie'
    )
    
    # Create products
    print("Creating products...")
    products = {
        'tomatoes': Product.objects.create(
            name='Organic Tomatoes', category=categories['produce'], supplier=supplier_fresh,
            unit_price=Decimal('3.50'), unit='kg', stock_quantity=150, reorder_level=50
        ),
        'lettuce': Product.objects.create(
            name='Fresh Lettuce', category=categories['produce'], supplier=supplier_fresh,
            unit_price=Decimal('2.00'), unit='kg', stock_quantity=80, reorder_level=30
        ),
        'milk': Product.objects.create(
            name='Whole Milk', category=categories['dairy'], supplier=supplier_fresh,
            unit_price=Decimal('1.50'), unit='liter', stock_quantity=200, reorder_level=100
        ),
        'cheese': Product.objects.create(
            name='Cheddar Cheese', category=categories['dairy'], supplier=supplier_fresh,
            unit_price=Decimal('12.00'), unit='kg', stock_quantity=45, reorder_level=20
        ),
        'chicken': Product.objects.create(
            name='Chicken Breast', category=categories['meat'], supplier=supplier_meat,
            unit_price=Decimal('8.50'), unit='kg', stock_quantity=100, reorder_level=40
        ),
        'beef': Product.objects.create(
            name='Beef Steak', category=categories['meat'], supplier=supplier_meat,
            unit_price=Decimal('18.00'), unit='kg', stock_quantity=60, reorder_level=25
        ),
    }
    
    # Create purchase orders
    print("Creating purchase orders...")
    po1 = PurchaseOrder.objects.create(
        order_number='202604250001',
        restaurant=restaurant1,
        supplier=supplier_fresh,
        status='APPROVED',
        delivery_date=datetime.now().date() + timedelta(days=3),
        notes='Weekly produce order',
        created_by=manager1
    )
    
    OrderItem.objects.create(purchase_order=po1, product=products['tomatoes'], quantity=20, unit_price=Decimal('3.50'))
    OrderItem.objects.create(purchase_order=po1, product=products['lettuce'], quantity=15, unit_price=Decimal('2.00'))
    OrderItem.objects.create(purchase_order=po1, product=products['milk'], quantity=30, unit_price=Decimal('1.50'))
    
    po2 = PurchaseOrder.objects.create(
        order_number='202604250002',
        restaurant=restaurant1,
        supplier=supplier_meat,
        status='FULFILLED',
        delivery_date=datetime.now().date() + timedelta(days=1),
        notes='Meat order for weekend',
        created_by=manager1
    )
    
    OrderItem.objects.create(purchase_order=po2, product=products['chicken'], quantity=25, unit_price=Decimal('8.50'))
    OrderItem.objects.create(purchase_order=po2, product=products['beef'], quantity=10, unit_price=Decimal('18.00'))
    
    # Create invoices
    print("Creating invoices...")
    invoice1 = Invoice.objects.create(
        invoice_number='INV202604250001',
        purchase_order=po2,
        restaurant=restaurant1,
        supplier=supplier_meat,
        issue_date=datetime.now().date(),
        due_date=datetime.now().date() + timedelta(days=30),
        status='PAID',
        subtotal=Decimal('392.50'),
        tax_rate=Decimal('13.50'),
        discount=Decimal('0.00'),
        notes='Payment received in full',
        created_by=supplier1
    )
    
    InvoiceItem.objects.create(invoice=invoice1, product=products['chicken'], description='Chicken Breast', quantity=25, unit_price=Decimal('8.50'))
    InvoiceItem.objects.create(invoice=invoice1, product=products['beef'], description='Beef Steak', quantity=10, unit_price=Decimal('18.00'))
    
    Payment.objects.create(
        invoice=invoice1,
        amount=Decimal('445.48'),
        payment_date=datetime.now().date() + timedelta(days=1),
        payment_method='BANK',
        reference_number='TRF20260426001',
        processed_by=accountant1
    )
    
    invoice2 = Invoice.objects.create(
        invoice_number='INV202604250002',
        purchase_order=po1,
        restaurant=restaurant1,
        supplier=supplier_fresh,
        issue_date=datetime.now().date(),
        due_date=datetime.now().date() + timedelta(days=15),
        status='PENDING',
        subtotal=Decimal('145.00'),
        tax_rate=Decimal('13.50'),
        discount=Decimal('10.00'),
        created_by=supplier1
    )
    
    InvoiceItem.objects.create(invoice=invoice2, product=products['tomatoes'], description='Organic Tomatoes', quantity=20, unit_price=Decimal('3.50'))
    InvoiceItem.objects.create(invoice=invoice2, product=products['lettuce'], description='Fresh Lettuce', quantity=15, unit_price=Decimal('2.00'))
    InvoiceItem.objects.create(invoice=invoice2, product=products['milk'], description='Whole Milk', quantity=30, unit_price=Decimal('1.50'))
    
    # Create deliveries
    print("Creating deliveries...")
    delivery1 = Delivery.objects.create(
        delivery_number='DEL202604250001',
        purchase_order=po2,
        driver=driver1,
        status='DELIVERED',
        scheduled_date=datetime.now() + timedelta(days=1, hours=10),
        actual_delivery_date=datetime.now() + timedelta(days=1, hours=10, minutes=30)
    )
    
    DeliveryItem.objects.create(delivery=delivery1, product=products['chicken'], quantity=25)
    DeliveryItem.objects.create(delivery=delivery1, product=products['beef'], quantity=10)
    
    delivery2 = Delivery.objects.create(
        delivery_number='DEL202604250002',
        purchase_order=po1,
        driver=driver1,
        status='IN_TRANSIT',
        scheduled_date=datetime.now() + timedelta(days=3, hours=9)
    )
    
    DeliveryItem.objects.create(delivery=delivery2, product=products['tomatoes'], quantity=20)
    DeliveryItem.objects.create(delivery=delivery2, product=products['lettuce'], quantity=15)
    DeliveryItem.objects.create(delivery=delivery2, product=products['milk'], quantity=30)
    
    # Create support cases
    print("Creating support cases...")
    case1 = SupportCase.objects.create(
        case_number='CASE202604250001',
        restaurant=restaurant1,
        subject='Quality issue with tomatoes',
        description='Some of the tomatoes in the last delivery were overripe.',
        status='RESOLVED',
        priority='MEDIUM',
        created_by=manager1,
        assigned_to=supplier1,
        resolved_at=datetime.now() + timedelta(days=1, hours=14)
    )
    
    CaseResponse.objects.create(
        case=case1,
        user=supplier1,
        message='We apologize for the quality issue. A credit will be applied to your next invoice.'
    )
    
    CaseResponse.objects.create(
        case=case1,
        user=manager1,
        message='Thank you for the quick response and resolution.'
    )
    
    case2 = SupportCase.objects.create(
        case_number='CASE202604250002',
        restaurant=restaurant1,
        subject='Delivery time change request',
        description='Can we reschedule tomorrow\'s delivery to 8 AM instead?',
        status='IN_PROGRESS',
        priority='HIGH',
        created_by=manager1,
        assigned_to=warehouse1
    )
    
    CaseResponse.objects.create(
        case=case2,
        user=warehouse1,
        message='Let me check with the driver and get back to you shortly.'
    )
    
    print("\nAll demo data loaded successfully!")

if __name__ == '__main__':
    load_data()
