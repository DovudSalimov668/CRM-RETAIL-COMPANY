# ============================================
# FILE 2: crm/urls.py - COMPLETE CODE
# ============================================

from django.urls import path
from . import views

urlpatterns = [
    # Public URLs
    path('register/', views.customer_register, name='customer_register'),
    path('login/', views.customer_login_view, name='customer_login'),
    path('logout/', views.customer_logout_view, name='customer_logout'),
    path('staff/login/', views.staff_login_view, name='staff_login'),
    path('staff/logout/', views.staff_logout_view, name='staff_logout'),
    path('auth/', views.login_choice, name='login_choice'),
    
    # Staff Registration (only for superusers)
    path('staff/register/', views.staff_register, name='staff_register'),
    
    # Customer Portal
    path('portal/', views.customer_portal, name='customer_portal'),
    
    # Customer Shopping
    path('shop/', views.product_catalog, name='product_catalog'),
    path('shop/product/<int:pk>/', views.product_detail_customer, name='product_detail_customer'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Customer Orders
    path('my-orders/', views.customer_order_history, name='customer_order_history'),
    path('my-orders/<int:pk>/', views.customer_order_detail, name='customer_order_detail'),
    path('profile/edit/', views.customer_profile_edit, name='customer_profile_edit'),
    
    # Public Home and Docs
    path('', views.home, name='home'),
    path('docs/', views.docs, name='docs'),
    path('docs/staff/', views.docs_staff, name='docs_staff'),
    path('docs/customer/', views.docs_customer, name='docs_customer'),

    # Admin Dashboard & Reports
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reports/', views.reports_view, name='reports'),
    
    # Customer Management
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/update/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('customers/export/', views.customer_export_csv, name='customer_export_csv'),
    
    # Order Management
    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/update/', views.order_update, name='order_update'),
    path('orders/<int:pk>/delete/', views.order_delete, name='order_delete'),
    
    # Product Management
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/update/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Task Management
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/update/', views.task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    
    # Deal Management
    path('deals/', views.deal_list, name='deal_list'),
    path('deals/create/', views.deal_create, name='deal_create'),
    path('deals/<int:pk>/', views.deal_detail, name='deal_detail'),
    path('deals/<int:pk>/update/', views.deal_update, name='deal_update'),
    
    # Quote Management
    path('quotes/', views.quote_list, name='quote_list'),
    path('quotes/create/', views.quote_create, name='quote_create'),
    path('quotes/<int:pk>/', views.quote_detail, name='quote_detail'),
    path('quotes/<int:pk>/update/', views.quote_update, name='quote_update'),
    
    # Enhanced CRM Features
    # Customer Segmentation
    path('segments/', views.segment_list, name='segment_list'),
    path('segments/create/', views.segment_create, name='segment_create'),
    path('segments/<int:pk>/', views.segment_detail, name='segment_detail'),
    
    # Marketing Campaigns
    path('campaigns/', views.campaign_list, name='campaign_list'),
    path('campaigns/create/', views.campaign_create, name='campaign_create'),
    path('campaigns/<int:pk>/', views.campaign_detail, name='campaign_detail'),
    
    # Support Tickets
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.ticket_create, name='ticket_create'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/<int:pk>/update/', views.ticket_update, name='ticket_update'),
    
    # Loyalty Programs
    path('loyalty/', views.loyalty_list, name='loyalty_list'),
    path('loyalty/<int:pk>/', views.loyalty_detail, name='loyalty_detail'),
    
    # Customer Feedback
    path('feedback/', views.feedback_list, name='feedback_list'),
    path('feedback/<int:pk>/', views.feedback_detail, name='feedback_detail'),
    
    # Automation Workflows
    path('workflows/', views.workflow_list, name='workflow_list'),
    path('workflows/create/', views.workflow_create, name='workflow_create'),
    path('workflows/<int:pk>/', views.workflow_detail, name='workflow_detail'),
    
    # Analytics
    path('rfm-analysis/', views.rfm_analysis, name='rfm_analysis'),
    path('cart-abandonment/', views.cart_abandonment_list, name='cart_abandonment_list'),
]
    