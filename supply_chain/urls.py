from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Purchase Orders
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/create/', views.purchase_order_create, name='purchase_order_create'),
    path('purchase-orders/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('purchase-orders/<int:pk>/add-item/', views.purchase_order_add_item, name='purchase_order_add_item'),
    path('purchase-orders/<int:pk>/submit/', views.purchase_order_submit, name='purchase_order_submit'),
    path('purchase-orders/<int:pk>/approve/', views.purchase_order_approve, name='purchase_order_approve'),
    
    # Invoices (MUST-HAVE)
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/add-item/', views.invoice_add_item, name='invoice_add_item'),
    
    # Payments
    path('invoices/<int:invoice_pk>/payment/', views.payment_create, name='payment_create'),
    
    # Products/Inventory
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    
    # Deliveries
    path('deliveries/', views.delivery_list, name='delivery_list'),
    path('deliveries/create/<int:po_pk>/', views.delivery_create, name='delivery_create'),
    path('deliveries/<int:pk>/', views.delivery_detail, name='delivery_detail'),
    path('deliveries/<int:pk>/update-status/', views.delivery_update_status, name='delivery_update_status'),
    
    # Support Cases
    path('support/', views.support_case_list, name='support_case_list'),
    path('support/create/', views.support_case_create, name='support_case_create'),
    path('support/<int:pk>/', views.support_case_detail, name='support_case_detail'),
    path('support/<int:pk>/resolve/', views.support_case_resolve, name='support_case_resolve'),
    
    # Reports
    path('reports/', views.reports_view, name='reports'),
]
