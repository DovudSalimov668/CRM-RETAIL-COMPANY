# ============================================
# VIEWS.PY - Complete CRM Views
# ============================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Sum, Count, Avg, Max, Min, F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django import forms
from datetime import datetime, timedelta
from decimal import Decimal
import csv
import json
import uuid
from .models import (
    Customer, Order, Interaction, Product, OrderItem, Task, Deal, Quote,
    CustomerSegment, CustomerRFM, CommunicationPreference, MarketingCampaign,
    LoyaltyProgram, LoyaltyTransaction, SupportTicket, TicketMessage,
    CustomerFeedback, AutomationWorkflow, CartAbandonment, CustomerAnalytics
)
from .forms import (
    CustomerForm, OrderForm, InteractionForm, CustomerRegistrationForm, 
    StaffRegistrationForm, TaskForm, DealForm, QuoteForm, ProductForm,
    CustomerSegmentForm, MarketingCampaignForm, SupportTicketForm, TicketMessageForm,
    CustomerFeedbackForm, AutomationWorkflowForm, CommunicationPreferenceForm
)
from .services import (
    calculate_rfm_scores, calculate_customer_analytics, execute_automation_workflow,
    award_loyalty_points, track_cart_abandonment
)

staff_login_required = login_required(login_url='staff_login')
customer_login_required = login_required(login_url='customer_login')

# ============================================
# PUBLIC PAGES
# ============================================

def home(request):
    context = {}
    if request.user.is_authenticated:
        context['is_staff'] = request.user.is_staff
    return render(request, 'crm/home.html', context)


def docs(request):
    return render(request, 'crm/docs.html')

def docs_staff(request):
    return render(request, 'crm/docs_staff.html')

def docs_customer(request):
    return render(request, 'crm/docs_customer.html')

# ============================================
# DASHBOARD & REPORTS
# ============================================

@staff_login_required
def dashboard(request):
    """Enhanced Admin dashboard with analytics"""
    if not request.user.is_staff:
        try:
            customer = request.user.customer_profile
            return redirect('customer_portal')
        except Customer.DoesNotExist:
            messages.error(request, 'Customer profile not found.')
            return redirect('customer_login')
    
    # Basic Statistics
    total_customers = Customer.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_deals = Deal.objects.count()
    total_tasks = Task.objects.filter(status='pending').count()
    
    # Revenue Statistics
    this_month = timezone.now().replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    this_month_revenue = Order.objects.filter(created_at__gte=this_month).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    last_month_revenue = Order.objects.filter(created_at__gte=last_month, created_at__lt=this_month).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Order Statistics
    pending_orders = Order.objects.filter(status='pending').count()
    processing_orders = Order.objects.filter(status='processing').count()
    delivered_orders = Order.objects.filter(status='delivered').count()
    
    # Customer Statistics
    active_customers = Customer.objects.filter(status='active').count()
    leads = Customer.objects.filter(status='lead').count()
    vip_customers = Customer.objects.filter(status='vip').count()
    
    # Deal Statistics
    total_deal_value = Deal.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    weighted_deal_value = sum([deal.get_weighted_value() for deal in Deal.objects.all()])
    closed_won = Deal.objects.filter(stage='closed_won').count()
    open_deals = Deal.objects.exclude(stage__in=['closed_won', 'closed_lost']).count()
    
    # Recent Activity
    recent_customers = Customer.objects.all()[:5]
    recent_orders = Order.objects.select_related('customer').all()[:5]
    recent_deals = Deal.objects.select_related('customer').all()[:5]
    upcoming_tasks = Task.objects.filter(status__in=['pending', 'in_progress']).order_by('due_date')[:5]
    
    # Monthly Revenue Chart Data (last 6 months)
    monthly_revenue = []
    for i in range(6):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        revenue = Order.objects.filter(created_at__gte=month_start, created_at__lte=month_end).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        monthly_revenue.append({
            'month': month_start.strftime('%b %Y'),
            'revenue': float(revenue)
        })
    monthly_revenue.reverse()
    
    # Customer Status Distribution
    customer_status_data = Customer.objects.values('status').annotate(count=Count('id')).order_by('status')
    
    # Order Status Distribution
    order_status_data = Order.objects.values('status').annotate(count=Count('id')).order_by('status')
    
    context = {
        'total_customers': total_customers,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_deals': total_deals,
        'total_tasks': total_tasks,
        'this_month_revenue': this_month_revenue,
        'last_month_revenue': last_month_revenue,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'delivered_orders': delivered_orders,
        'active_customers': active_customers,
        'leads': leads,
        'vip_customers': vip_customers,
        'total_deal_value': total_deal_value,
        'weighted_deal_value': weighted_deal_value,
        'closed_won': closed_won,
        'open_deals': open_deals,
        'recent_customers': recent_customers,
        'recent_orders': recent_orders,
        'recent_deals': recent_deals,
        'upcoming_tasks': upcoming_tasks,
        'monthly_revenue': json.dumps(monthly_revenue),
        'customer_status_data': json.dumps(list(customer_status_data)),
        'order_status_data': json.dumps(list(order_status_data)),
    }
    return render(request, 'crm/dashboard.html', context)


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def reports_view(request):
    """Reports and Analytics View"""
    # Sales Report
    sales_data = Order.objects.values('created_at__date').annotate(
        total=Sum('total_amount'),
        count=Count('id')
    ).order_by('created_at__date')[:30]
    
    # Top Customers
    top_customers = Customer.objects.annotate(
        total_orders=Count('orders'),
        total_spent=Sum('orders__total_amount')
    ).order_by('-total_spent')[:10]
    
    # Product Performance
    product_performance = Product.objects.annotate(
        times_ordered=Count('orderitem'),
        total_quantity=Sum('orderitem__quantity')
    ).order_by('-times_ordered')[:10]
    
    # Deal Pipeline
    deal_pipeline = Deal.objects.values('stage').annotate(
        count=Count('id'),
        total_amount=Sum('amount')
    ).order_by('stage')
    
    context = {
        'sales_data': sales_data,
        'top_customers': top_customers,
        'product_performance': product_performance,
        'deal_pipeline': deal_pipeline,
    }
    return render(request, 'crm/reports.html', context)


# ============================================
# CUSTOMER MANAGEMENT
# ============================================

@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def customer_list(request):
    """Customer list view with pagination and search"""
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    source_filter = request.GET.get('source', '')
    page = request.GET.get('page', 1)
    
    customers = Customer.objects.select_related('assigned_to', 'created_by').all()
    
    if query:
        customers = customers.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(company_name__icontains=query)
        )
    
    if status_filter:
        customers = customers.filter(status=status_filter)
    
    if source_filter:
        customers = customers.filter(source=source_filter)
    
    customers = customers.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(customers, 25)
    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)
    
    context = {
        'customers': customers,
        'query': query,
        'status_filter': status_filter,
        'source_filter': source_filter,
    }
    return render(request, 'crm/customer_list.html', context)


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def customer_detail(request, pk):
    """Customer detail view with orders, interactions, deals, tasks"""
    customer = get_object_or_404(Customer, pk=pk)
    orders = customer.orders.all().order_by('-created_at')[:10]
    interactions = customer.interactions.all().order_by('-created_at')[:10]
    deals = customer.deals.all().order_by('-created_at')
    tasks = customer.tasks.all().order_by('-due_date')[:10]
    quotes = customer.quotes.all().order_by('-created_at')[:10]
    
    # Statistics
    total_spent = customer.get_total_spent()
    total_orders = customer.orders.count()
    avg_order_value = total_spent / total_orders if total_orders > 0 else 0
    
    if request.method == 'POST':
        form = InteractionForm(request.POST)
        if form.is_valid():
            interaction = form.save(commit=False)
            interaction.customer = customer
            interaction.created_by = request.user
            interaction.save()
            messages.success(request, 'Interaction added successfully!')
            return redirect('customer_detail', pk=pk)
    else:
        form = InteractionForm()
    
    context = {
        'customer': customer,
        'orders': orders,
        'interactions': interactions,
        'deals': deals,
        'tasks': tasks,
        'quotes': quotes,
        'form': form,
        'total_spent': total_spent,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
    }
    return render(request, 'crm/customer_detail.html', context)


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def customer_create(request):
    """Customer create view"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_by = request.user
            customer.save()
            messages.success(request, 'Customer created successfully!')
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm()
    
    return render(request, 'crm/customer_form.html', {'form': form, 'action': 'Create'})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def customer_update(request, pk):
    """Customer update view"""
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('customer_detail', pk=pk)
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'crm/customer_form.html', {'form': form, 'action': 'Update'})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def customer_delete(request, pk):
    """Customer delete view"""
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully!')
        return redirect('customer_list')
    return render(request, 'crm/customer_confirm_delete.html', {'customer': customer})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def customer_export_csv(request):
    """Export customers to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['First Name', 'Last Name', 'Email', 'Phone', 'Status', 'Source', 'Company', 'Total Orders', 'Total Spent'])
    
    customers = Customer.objects.annotate(
        total_orders=Count('orders'),
        total_spent=Sum('orders__total_amount')
    )
    
    for customer in customers:
        writer.writerow([
            customer.first_name,
            customer.last_name,
            customer.email,
            customer.phone,
            customer.get_status_display(),
            customer.get_source_display(),
            customer.company_name,
            customer.total_orders,
            customer.total_spent or 0
        ])
    
    return response


# ============================================
# ORDER MANAGEMENT
# ============================================

@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def order_list(request):
    """Order list view with pagination"""
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    payment_filter = request.GET.get('payment_status', '')
    page = request.GET.get('page', 1)
    
    orders = Order.objects.select_related('customer', 'created_by').all()
    
    if query:
        orders = orders.filter(
            Q(order_number__icontains=query) |
            Q(customer__first_name__icontains=query) |
            Q(customer__last_name__icontains=query) |
            Q(customer__email__icontains=query)
        )
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if payment_filter:
        orders = orders.filter(payment_status=payment_filter)
    
    orders = orders.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 25)
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    
    context = {
        'orders': orders,
        'query': query,
        'status_filter': status_filter,
        'payment_filter': payment_filter,
    }
    return render(request, 'crm/order_list.html', context)


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def order_detail(request, pk):
    """Order detail view with items"""
    order = get_object_or_404(Order, pk=pk)
    order_items = order.items.select_related('product').all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'crm/order_detail.html', context)


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def order_create(request):
    """Order create view"""
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            # Calculate total
            order.calculate_total()
            order.save()
            messages.success(request, 'Order created successfully!')
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm()
    
    return render(request, 'crm/order_form.html', {'form': form, 'action': 'Create'})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def order_update(request, pk):
    """Order update view"""
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save(commit=False)
            order.calculate_total()
            order.save()
            messages.success(request, 'Order updated successfully!')
            return redirect('order_detail', pk=pk)
    else:
        form = OrderForm(instance=order)
    
    return render(request, 'crm/order_form.html', {'form': form, 'action': 'Update', 'order': order})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def order_delete(request, pk):
    """Order delete view"""
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Order deleted successfully!')
        return redirect('order_list')
    return render(request, 'crm/order_confirm_delete.html', {'order': order})


# ============================================
# PRODUCT MANAGEMENT
# ============================================

@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def product_list(request):
    """Product list view with pagination"""
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    low_stock = request.GET.get('low_stock', '')
    page = request.GET.get('page', 1)
    
    products = Product.objects.all()
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query) |
            Q(description__icontains=query)
        )
    
    if category_filter:
        products = products.filter(category=category_filter)
    
    if low_stock:
        products = products.filter(stock_quantity__lte=F('min_stock_level'))
    
    products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 25)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'products': products,
        'query': query,
        'category_filter': category_filter,
        'low_stock': low_stock,
    }
    return render(request, 'crm/product_list.html', context)


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def product_create(request):
    """Product create view"""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()
    
    return render(request, 'crm/product_form.html', {'form': form, 'action': 'Create'})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def product_update(request, pk):
    """Product update view"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'crm/product_form.html', {'form': form, 'action': 'Update'})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def product_delete(request, pk):
    """Product delete view"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('product_list')
    return render(request, 'crm/product_confirm_delete.html', {'product': product})


# ============================================
# TASK MANAGEMENT
# ============================================

@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def task_list(request):
    """Task list view with pagination and filters"""
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    assigned_to_filter = request.GET.get('assigned_to', '')
    overdue = request.GET.get('overdue', '')
    page = request.GET.get('page', 1)
    
    tasks = Task.objects.select_related('customer', 'assigned_to', 'created_by').all()
    
    if query:
        tasks = tasks.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(customer__first_name__icontains=query) |
            Q(customer__last_name__icontains=query)
        )
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    if assigned_to_filter:
        tasks = tasks.filter(assigned_to_id=assigned_to_filter)
    
    if overdue:
        tasks = tasks.filter(status__in=['pending', 'in_progress'], due_date__lt=timezone.now())
    
    tasks = tasks.order_by('due_date', '-priority')
    
    # Pagination
    paginator = Paginator(tasks, 25)
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)
    
    # Get all staff for filter
    staff_members = User.objects.filter(is_staff=True)
    
    context = {
        'tasks': tasks,
        'query': query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'assigned_to_filter': assigned_to_filter,
        'overdue': overdue,
        'staff_members': staff_members,
    }
    return render(request, 'crm/task_list.html', context)


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def task_create(request):
    """Task create view"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('task_list')
    else:
        form = TaskForm(initial={'assigned_to': request.user})
    
    return render(request, 'crm/task_form.html', {'form': form, 'action': 'Create'})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def task_update(request, pk):
    """Task update view"""
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            if task.status == 'completed' and not task.completed_at:
                task.completed_at = timezone.now()
            elif task.status != 'completed':
                task.completed_at = None
            task.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'crm/task_form.html', {'form': form, 'action': 'Update'})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def task_delete(request, pk):
    """Task delete view"""
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('task_list')
    return render(request, 'crm/task_confirm_delete.html', {'task': task})


# ============================================
# DEAL MANAGEMENT
# ============================================

@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def deal_list(request):
    """Deal list view with pagination"""
    query = request.GET.get('q', '')
    stage_filter = request.GET.get('stage', '')
    assigned_to_filter = request.GET.get('assigned_to', '')
    page = request.GET.get('page', 1)
    
    deals = Deal.objects.select_related('customer', 'assigned_to').all()
    
    if query:
        deals = deals.filter(
            Q(title__icontains=query) |
            Q(customer__first_name__icontains=query) |
            Q(customer__last_name__icontains=query) |
            Q(description__icontains=query)
        )
    
    if stage_filter:
        deals = deals.filter(stage=stage_filter)
    
    if assigned_to_filter:
        deals = deals.filter(assigned_to_id=assigned_to_filter)
    
    deals = deals.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(deals, 25)
    try:
        deals = paginator.page(page)
    except PageNotAnInteger:
        deals = paginator.page(1)
    except EmptyPage:
        deals = paginator.page(paginator.num_pages)
    
    # Get all staff for filter
    staff_members = User.objects.filter(is_staff=True)
    
    context = {
        'deals': deals,
        'query': query,
        'stage_filter': stage_filter,
        'assigned_to_filter': assigned_to_filter,
        'staff_members': staff_members,
    }
    return render(request, 'crm/deal_list.html', context)


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def deal_detail(request, pk):
    """Deal detail view"""
    deal = get_object_or_404(Deal, pk=pk)
    quotes = deal.quotes.all().order_by('-created_at')
    
    context = {
        'deal': deal,
        'quotes': quotes,
    }
    return render(request, 'crm/deal_detail.html', context)


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def deal_create(request):
    """Deal create view"""
    if request.method == 'POST':
        form = DealForm(request.POST)
        if form.is_valid():
            deal = form.save(commit=False)
            if deal.stage == 'closed_won' and not deal.closed_at:
                deal.closed_at = timezone.now()
            deal.save()
            messages.success(request, 'Deal created successfully!')
            return redirect('deal_detail', pk=deal.pk)
    else:
        form = DealForm(initial={'assigned_to': request.user})
    
    return render(request, 'crm/deal_form.html', {'form': form, 'action': 'Create'})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def deal_update(request, pk):
    """Deal update view"""
    deal = get_object_or_404(Deal, pk=pk)
    if request.method == 'POST':
        form = DealForm(request.POST, instance=deal)
        if form.is_valid():
            deal = form.save(commit=False)
            if deal.stage == 'closed_won' and not deal.closed_at:
                deal.closed_at = timezone.now()
            elif deal.stage not in ['closed_won', 'closed_lost']:
                deal.closed_at = None
            deal.save()
            messages.success(request, 'Deal updated successfully!')
            return redirect('deal_detail', pk=pk)
    else:
        form = DealForm(instance=deal)
    
    return render(request, 'crm/deal_form.html', {'form': form, 'action': 'Update'})


# ============================================
# QUOTE MANAGEMENT
# ============================================

@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def quote_list(request):
    """Quote list view with pagination"""
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    customer_filter = request.GET.get('customer', '')
    expired = request.GET.get('expired', '')
    page = request.GET.get('page', 1)
    
    quotes = Quote.objects.select_related('customer', 'deal', 'created_by').all()
    
    if query:
        quotes = quotes.filter(
            Q(quote_number__icontains=query) |
            Q(customer__first_name__icontains=query) |
            Q(customer__last_name__icontains=query)
        )
    
    if status_filter:
        quotes = quotes.filter(status=status_filter)
    
    if customer_filter:
        quotes = quotes.filter(customer_id=customer_filter)
    
    if expired:
        from datetime import date
        quotes = quotes.filter(valid_until__lt=date.today(), status__in=['draft', 'sent'])
    
    quotes = quotes.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(quotes, 25)
    try:
        quotes = paginator.page(page)
    except PageNotAnInteger:
        quotes = paginator.page(1)
    except EmptyPage:
        quotes = paginator.page(paginator.num_pages)
    
    context = {
        'quotes': quotes,
        'query': query,
        'status_filter': status_filter,
        'customer_filter': customer_filter,
        'expired': expired,
    }
    return render(request, 'crm/quote_list.html', context)


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def quote_detail(request, pk):
    """Quote detail view"""
    quote = get_object_or_404(Quote, pk=pk)
    
    context = {
        'quote': quote,
    }
    return render(request, 'crm/quote_detail.html', context)


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def quote_create(request):
    """Quote create view"""
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.created_by = request.user
            # Calculate total
            quote.total_amount = quote.subtotal + quote.tax - quote.discount
            quote.save()
            messages.success(request, 'Quote created successfully!')
            return redirect('quote_detail', pk=quote.pk)
    else:
        form = QuoteForm()
    
    return render(request, 'crm/quote_form.html', {'form': form, 'action': 'Create'})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def quote_update(request, pk):
    """Quote update view"""
    quote = get_object_or_404(Quote, pk=pk)
    if request.method == 'POST':
        form = QuoteForm(request.POST, instance=quote)
        if form.is_valid():
            quote = form.save(commit=False)
            # Calculate total
            quote.total_amount = quote.subtotal + quote.tax - quote.discount
            quote.save()
            messages.success(request, 'Quote updated successfully!')
            return redirect('quote_detail', pk=pk)
    else:
        form = QuoteForm(instance=quote)
    
    return render(request, 'crm/quote_form.html', {'form': form, 'action': 'Update'})


# ============================================
# AUTHENTICATION VIEWS
# ============================================


def staff_login_view(request):
    """Staff/admin login view with email, password, and OTP"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard')

    from .otp_service import create_and_send_otp, verify_otp

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        otp_code = request.POST.get('otp_code', '').strip()
        action = request.POST.get('action', '')

        if action == 'send_otp':
            try:
                user = User.objects.get(email=email)
                if not user.is_staff:
                    messages.error(request, 'This account does not have staff access. Please use the customer login page.')
                    return redirect('customer_login')
                user_auth = authenticate(request, username=user.username, password=password)
                if not user_auth:
                    messages.error(request, 'Invalid password.')
                    return render(request, 'crm/staff_login.html', {'email': '', 'msg_type': 'password_error'})
                otp = create_and_send_otp(email, user)
                if otp:
                    messages.success(request, 'OTP code has been sent to your email. Please check your inbox.')
                    request.session['login_email'] = email
                    request.session['login_type'] = 'staff'
                else:
                    messages.error(request, 'Failed to send OTP. Please try again or contact support.')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')

        elif action == 'verify_otp':
            email = request.session.get('login_email', '')
            if not email:
                messages.error(request, 'Please request an OTP first.')
                return redirect('staff_login')

            user = verify_otp(email, otp_code)
            if user:
                if not user.is_staff:
                    messages.error(request, 'This account does not have staff access.')
                    del request.session['login_email']
                    del request.session['login_type']
                    return redirect('customer_login')
                auth_login(request, user)
                del request.session['login_email']
                del request.session['login_type']
                messages.success(request, f'Welcome back, {user.get_full_name() or user.email}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid or expired OTP code. Please try again.')

        if action == 'resend_otp':
            email = request.session.get('login_email', '')
            if not email:
                messages.error(request, 'Please request an OTP first.')
                return redirect('staff_login')
            try:
                user = User.objects.get(email=email)
                if not user.is_staff:
                    messages.error(request, 'This account does not have staff access. Please use the customer login page.')
                    return redirect('customer_login')
                otp = create_and_send_otp(email, user)
                if otp:
                    messages.success(request, 'OTP code has been re-sent to your email.')
                else:
                    messages.error(request, 'Failed to resend OTP. Please try again or contact support.')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
            except Exception as e:
                messages.error(request, f'An error occurred while resending OTP: {str(e)}')

    return render(request, 'crm/staff_login.html', {
        'email': request.session.get('login_email', '')
    })


@staff_login_required
def staff_logout_view(request):
    """Staff logout view"""
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('staff_login')


def login_choice(request):
    """Landing to choose Staff vs Customer login"""
    if request.user.is_authenticated:
        return redirect('dashboard' if request.user.is_staff else 'customer_portal')
    return render(request, 'crm/auth_choice.html')


def customer_register(request):
    """Customer registration view"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard')
        else:
            return redirect('customer_portal')
    
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create Customer profile
            customer = Customer.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                company_name=form.cleaned_data.get('company_name', ''),
                status='active',
                created_by=user
            )
            
            # Set user email
            user.email = form.cleaned_data['email']
            user.save()
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('customer_login')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'crm/register.html', {'form': form})


def customer_login_view(request):
    """Customer login view with email, password, and OTP"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard')
        else:
            return redirect('customer_portal')

    from .otp_service import create_and_send_otp, verify_otp

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        otp_code = request.POST.get('otp_code', '').strip()
        action = request.POST.get('action', '')

        if action == 'send_otp':
            try:
                user = User.objects.get(email=email)
                if user.is_staff:
                    messages.error(request, 'Please use the staff login page to access the admin portal.')
                    return redirect('staff_login')
                user_auth = authenticate(request, username=user.username, password=password)
                if not user_auth:
                    messages.error(request, 'Invalid password.')
                    return render(request, 'crm/login.html', {'email': '', 'msg_type': 'password_error'})
                otp = create_and_send_otp(email, user)
                if otp:
                    messages.success(request, 'OTP code has been sent to your email. Please check your inbox.')
                    request.session['login_email'] = email
                    request.session['login_type'] = 'customer'
                else:
                    messages.error(request, 'Failed to send OTP. Please try again or contact support.')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')

        elif action == 'verify_otp':
            email = request.session.get('login_email', '')
            if not email:
                messages.error(request, 'Please request an OTP first.')
                return redirect('customer_login')

            user = verify_otp(email, otp_code)
            if user:
                if user.is_staff:
                    messages.error(request, 'Please use the staff login page.')
                    del request.session['login_email']
                    del request.session['login_type']
                    return redirect('staff_login')
                auth_login(request, user)
                del request.session['login_email']
                del request.session['login_type']
                messages.success(request, f'Welcome back, {user.get_full_name() or user.email}!')
                return redirect('customer_portal')
            else:
                messages.error(request, 'Invalid or expired OTP code. Please try again.')

        if action == 'resend_otp':
            email = request.session.get('login_email', '')
            if not email:
                messages.error(request, 'Please request an OTP first.')
                return redirect('customer_login')
            try:
                user = User.objects.get(email=email)
                if user.is_staff:
                    messages.error(request, 'Please use the staff login page to access the admin portal.')
                    return redirect('staff_login')
                otp = create_and_send_otp(email, user)
                if otp:
                    messages.success(request, 'OTP code has been re-sent to your email.')
                else:
                    messages.error(request, 'Failed to resend OTP. Please try again or contact support.')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
            except Exception as e:
                messages.error(request, f'An error occurred while resending OTP: {str(e)}')

    return render(request, 'crm/login.html', {
        'email': request.session.get('login_email', '')
    })


def customer_logout_view(request):
    """Customer logout view"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('staff_logout')
        auth_logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('customer_login')


@customer_login_required
def customer_portal(request):
    """Customer portal view - for logged-in customers"""
    try:
        customer = request.user.customer_profile
    except Customer.DoesNotExist:
        if request.user.is_staff:
            return redirect('dashboard')
        messages.error(request, 'Customer profile not found.')
        return redirect('customer_login')
    
    # Get customer's orders
    orders = customer.orders.all().order_by('-created_at')[:10]
    total_orders = customer.orders.count()
    total_spent = customer.get_total_spent()
    recent_interactions = customer.interactions.all().order_by('-created_at')[:5]
    deals = customer.deals.all().order_by('-created_at')[:5]
    quotes = customer.quotes.all().order_by('-created_at')[:5]
    
    context = {
        'customer': customer,
        'orders': orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'recent_interactions': recent_interactions,
        'deals': deals,
        'quotes': quotes,
    }
    
    return render(request, 'crm/customer_portal.html', context)


@staff_login_required
@user_passes_test(lambda u: u.is_superuser)
def staff_register(request):
    """Staff registration view - only accessible to superusers"""
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Staff member {user.username} has been created successfully!')
            return redirect('dashboard')
    else:
        form = StaffRegistrationForm()
    
    return render(request, 'crm/staff_register.html', {'form': form})


# ============================================
# CUSTOMER-FACING SHOPPING VIEWS
# ============================================

def product_catalog(request):
    """Public product catalog for customers"""
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    page = request.GET.get('page', 1)
    
    products = Product.objects.filter(is_active=True, stock_quantity__gt=0)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(sku__icontains=query)
        )
    
    if category_filter:
        products = products.filter(category=category_filter)
    
    products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'products': products,
        'query': query,
        'category_filter': category_filter,
    }
    return render(request, 'crm/customer/product_catalog.html', context)


def product_detail_customer(request, pk):
    """Product detail view for customers"""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(pk=pk)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'crm/customer/product_detail.html', context)


def add_to_cart(request, product_id):
    """Add product to shopping cart"""
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to add items to cart.')
        return redirect('customer_login')
    
    try:
        customer = request.user.customer_profile
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('customer_login')
    
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        messages.error(request, 'Quantity must be greater than 0.')
        return redirect('product_detail_customer', pk=product_id)
    
    if product.stock_quantity < quantity:
        messages.error(request, f'Only {product.stock_quantity} items available in stock.')
        return redirect('product_detail_customer', pk=product_id)
    
    # Get or create cart in session
    cart = request.session.get('cart', {})
    product_key = str(product_id)
    
    if product_key in cart:
        cart[product_key]['quantity'] += quantity
    else:
        cart[product_key] = {
            'product_id': product_id,
            'name': product.name,
            'price': str(product.price),
            'quantity': quantity,
            'image_url': product.image_url,
        }
    
    request.session['cart'] = cart
    messages.success(request, f'{product.name} added to cart!')
    
    return redirect('view_cart')


def view_cart(request):
    """View shopping cart"""
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to view your cart.')
        return redirect('customer_login')
    
    cart = request.session.get('cart', {})
    cart_items = []
    subtotal = Decimal('0.00')
    
    for key, item in cart.items():
        try:
            product = Product.objects.get(pk=item['product_id'], is_active=True)
            quantity = int(item['quantity'])
            price = Decimal(item['price'])
            item_total = price * quantity
            subtotal += item_total
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'price': price,
                'total': item_total,
            })
        except Product.DoesNotExist:
            # Remove invalid items
            del cart[key]
            request.session['cart'] = cart
    
    # Calculate totals
    tax_rate = Decimal('0.10')  # 10% tax
    tax = subtotal * tax_rate
    shipping = Decimal('10.00') if subtotal < Decimal('100.00') else Decimal('0.00')
    total = subtotal + tax + shipping
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'crm/customer/cart.html', context)


def update_cart(request, product_id):
    """Update cart item quantity"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    cart = request.session.get('cart', {})
    product_key = str(product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if product_key in cart:
        if quantity <= 0:
            del cart[product_key]
        else:
            product = get_object_or_404(Product, pk=product_id)
            if product.stock_quantity >= quantity:
                cart[product_key]['quantity'] = quantity
            else:
                return JsonResponse({'error': f'Only {product.stock_quantity} available'}, status=400)
    
    request.session['cart'] = cart
    return redirect('view_cart')


def remove_from_cart(request, product_id):
    """Remove item from cart"""
    if not request.user.is_authenticated:
        return redirect('customer_login')
    
    cart = request.session.get('cart', {})
    product_key = str(product_id)
    
    if product_key in cart:
        del cart[product_key]
        request.session['cart'] = cart
        messages.success(request, 'Item removed from cart.')
    
    return redirect('view_cart')


@customer_login_required
def checkout(request):
    """Checkout process"""
    try:
        customer = request.user.customer_profile
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('customer_login')
    
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('product_catalog')
    
    # Calculate cart totals
    subtotal = Decimal('0.00')
    cart_items = []
    
    for key, item in cart.items():
        try:
            product = Product.objects.get(pk=item['product_id'], is_active=True)
            quantity = int(item['quantity'])
            price = Decimal(item['price'])
            item_total = price * quantity
            subtotal += item_total
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'price': price,
                'total': item_total,
            })
        except Product.DoesNotExist:
            messages.error(request, f'Product {item.get("name", "Unknown")} is no longer available.')
            return redirect('view_cart')
    
    tax_rate = Decimal('0.10')
    tax = subtotal * tax_rate
    shipping = Decimal('10.00') if subtotal < Decimal('100.00') else Decimal('0.00')
    total = subtotal + tax + shipping
    
    if request.method == 'POST':
        # Create order
        import uuid
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        order = Order.objects.create(
            customer=customer,
            order_number=order_number,
            status='pending',
            payment_status='unpaid',
            subtotal=subtotal,
            tax=tax,
            discount=Decimal('0.00'),
            shipping_cost=shipping,
            shipping_address=request.POST.get('shipping_address', customer.address or ''),
            notes=request.POST.get('notes', ''),
            created_by=request.user
        )
        order.calculate_total()
        
        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                unit_price=item['price'],
                discount=Decimal('0.00'),
            )
            
            # Update stock
            item['product'].stock_quantity -= item['quantity']
            item['product'].save()
        
        # Clear cart
        request.session['cart'] = {}
        
        # Execute automation workflows
        execute_automation_workflow('order_placed', customer=customer, order=order)
        
        # Award loyalty points (if payment is marked as paid)
        # In production, this would happen after payment confirmation
        # award_loyalty_points(customer, order)
        
        messages.success(request, f'Order {order_number} placed successfully!')
        return redirect('customer_order_detail', pk=order.pk)
    
    context = {
        'customer': customer,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'crm/customer/checkout.html', context)


@customer_login_required
def customer_order_history(request):
    """Customer order history with filters"""
    try:
        customer = request.user.customer_profile
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('customer_login')
    
    status_filter = request.GET.get('status', '')
    page = request.GET.get('page', 1)
    
    orders = customer.orders.all()
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    orders = orders.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 10)
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
    }
    return render(request, 'crm/customer/order_history.html', context)


@customer_login_required
def customer_order_detail(request, pk):
    """Customer order detail view"""
    try:
        customer = request.user.customer_profile
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('customer_login')
    
    order = get_object_or_404(Order, pk=pk, customer=customer)
    order_items = order.items.select_related('product').all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'crm/customer/order_detail.html', context)


@customer_login_required
def customer_profile_edit(request):
    """Customer profile editing"""
    try:
        customer = request.user.customer_profile
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('customer_login')
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('customer_portal')
    else:
        # Create a limited form for customers (only editable fields)
        form = CustomerForm(instance=customer)
        # Remove fields customers shouldn't edit
        for field in ['status', 'source', 'assigned_to', 'next_follow_up', 'tags']:
            if field in form.fields:
                form.fields[field].widget = forms.HiddenInput()
    
    context = {
        'form': form,
        'customer': customer,
    }
    return render(request, 'crm/customer/profile_edit.html', context)


# ============================================
# ENHANCED CRM FEATURES VIEWS
# ============================================

@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def segment_list(request):
    """List all customer segments"""
    segments = CustomerSegment.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(segments, 20)
    try:
        segments = paginator.page(page)
    except PageNotAnInteger:
        segments = paginator.page(1)
    except EmptyPage:
        segments = paginator.page(paginator.num_pages)
    return render(request, 'crm/segment_list.html', {'segments': segments})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def segment_create(request):
    """Create new customer segment"""
    if request.method == 'POST':
        form = CustomerSegmentForm(request.POST)
        if form.is_valid():
            segment = form.save()
            messages.success(request, f'Segment "{segment.name}" created successfully!')
            return redirect('segment_list')
    else:
        form = CustomerSegmentForm()
    return render(request, 'crm/segment_form.html', {'form': form, 'action': 'Create'})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def campaign_list(request):
    """List all marketing campaigns"""
    campaigns = MarketingCampaign.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(campaigns, 20)
    try:
        campaigns = paginator.page(page)
    except PageNotAnInteger:
        campaigns = paginator.page(1)
    except EmptyPage:
        campaigns = paginator.page(paginator.num_pages)
    return render(request, 'crm/campaign_list.html', {'campaigns': campaigns})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def campaign_create(request):
    """Create new marketing campaign"""
    if request.method == 'POST':
        form = MarketingCampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.created_by = request.user
            campaign.save()
            messages.success(request, f'Campaign "{campaign.name}" created successfully!')
            return redirect('campaign_list')
    else:
        form = MarketingCampaignForm()
    return render(request, 'crm/campaign_form.html', {'form': form, 'action': 'Create'})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def campaign_detail(request, pk):
    """View campaign details and analytics"""
    campaign = get_object_or_404(MarketingCampaign, pk=pk)
    return render(request, 'crm/campaign_detail.html', {'campaign': campaign})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def segment_detail(request, pk):
    """View segment details"""
    segment = get_object_or_404(CustomerSegment, pk=pk)
    customers = Customer.objects.filter(status='active')[:50]
    return render(request, 'crm/segment_detail.html', {'segment': segment, 'customers': customers})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def loyalty_detail(request, pk):
    """View loyalty program details"""
    loyalty = get_object_or_404(LoyaltyProgram, pk=pk)
    transactions = loyalty.transactions.all().order_by('-created_at')[:20]
    return render(request, 'crm/loyalty_detail.html', {
        'loyalty': loyalty,
        'transactions': transactions,
    })


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def feedback_detail(request, pk):
    """View feedback details"""
    feedback = get_object_or_404(CustomerFeedback, pk=pk)
    return render(request, 'crm/feedback_detail.html', {'feedback': feedback})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def workflow_detail(request, pk):
    """View workflow details"""
    workflow = get_object_or_404(AutomationWorkflow, pk=pk)
    return render(request, 'crm/workflow_detail.html', {'workflow': workflow})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def ticket_list(request):
    """List all support tickets"""
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    
    tickets = SupportTicket.objects.all()
    
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    
    tickets = tickets.order_by('-created_at')
    
    page = request.GET.get('page', 1)
    paginator = Paginator(tickets, 20)
    try:
        tickets = paginator.page(page)
    except PageNotAnInteger:
        tickets = paginator.page(1)
    except EmptyPage:
        tickets = paginator.page(paginator.num_pages)
    
    return render(request, 'crm/ticket_list.html', {
        'tickets': tickets,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    })


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def ticket_create(request):
    """Create new support ticket"""
    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.ticket_number = f"TKT-{uuid.uuid4().hex[:8].upper()}"
            ticket.created_by = request.user
            ticket.save()
            messages.success(request, f'Ticket {ticket.ticket_number} created successfully!')
            execute_automation_workflow('ticket_created', customer=ticket.customer, ticket=ticket)
            return redirect('ticket_detail', pk=ticket.pk)
    else:
        form = SupportTicketForm()
    return render(request, 'crm/ticket_form.html', {'form': form, 'action': 'Create'})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def ticket_detail(request, pk):
    """View ticket details and messages"""
    ticket = get_object_or_404(SupportTicket, pk=pk)
    messages_list = ticket.messages.all()
    
    if request.method == 'POST':
        message_form = TicketMessageForm(request.POST)
        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.ticket = ticket
            message.created_by = request.user
            message.save()
            
            if ticket.status == 'new' and not message.is_internal:
                ticket.status = 'open'
                if not ticket.first_response_time:
                    ticket.first_response_time = timezone.now()
                ticket.save()
            
            messages.success(request, 'Message added successfully!')
            return redirect('ticket_detail', pk=ticket.pk)
    else:
        message_form = TicketMessageForm()
    
    return render(request, 'crm/ticket_detail.html', {
        'ticket': ticket,
        'messages_list': messages_list,
        'message_form': message_form,
    })


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def ticket_update(request, pk):
    """Update support ticket"""
    ticket = get_object_or_404(SupportTicket, pk=pk)
    if request.method == 'POST':
        form = SupportTicketForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save()
            if ticket.status == 'resolved' and not ticket.resolution_time:
                ticket.resolution_time = timezone.now()
                ticket.save()
            messages.success(request, 'Ticket updated successfully!')
            return redirect('ticket_detail', pk=ticket.pk)
    else:
        form = SupportTicketForm(instance=ticket)
    return render(request, 'crm/ticket_form.html', {'form': form, 'action': 'Update', 'ticket': ticket})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def loyalty_list(request):
    """List all loyalty programs"""
    tier_filter = request.GET.get('tier', '')
    loyalty_programs = LoyaltyProgram.objects.all()
    
    if tier_filter:
        loyalty_programs = loyalty_programs.filter(tier=tier_filter)
    
    loyalty_programs = loyalty_programs.order_by('-lifetime_points')
    
    page = request.GET.get('page', 1)
    paginator = Paginator(loyalty_programs, 20)
    try:
        loyalty_programs = paginator.page(page)
    except PageNotAnInteger:
        loyalty_programs = paginator.page(1)
    except EmptyPage:
        loyalty_programs = paginator.page(paginator.num_pages)
    
    return render(request, 'crm/loyalty_list.html', {
        'loyalty_programs': loyalty_programs,
        'tier_filter': tier_filter,
    })


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def feedback_list(request):
    """List all customer feedback"""
    type_filter = request.GET.get('type', '')
    feedbacks = CustomerFeedback.objects.all()
    
    if type_filter:
        feedbacks = feedbacks.filter(feedback_type=type_filter)
    
    feedbacks = feedbacks.order_by('-created_at')
    
    page = request.GET.get('page', 1)
    paginator = Paginator(feedbacks, 20)
    try:
        feedbacks = paginator.page(page)
    except PageNotAnInteger:
        feedbacks = paginator.page(1)
    except EmptyPage:
        feedbacks = paginator.page(paginator.num_pages)
    
    return render(request, 'crm/feedback_list.html', {
        'feedbacks': feedbacks,
        'type_filter': type_filter,
    })


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def workflow_list(request):
    """List all automation workflows"""
    workflows = AutomationWorkflow.objects.all()
    return render(request, 'crm/workflow_list.html', {'workflows': workflows})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def workflow_create(request):
    """Create new automation workflow"""
    if request.method == 'POST':
        form = AutomationWorkflowForm(request.POST)
        if form.is_valid():
            workflow = form.save()
            messages.success(request, f'Workflow "{workflow.name}" created successfully!')
            return redirect('workflow_list')
    else:
        form = AutomationWorkflowForm()
    return render(request, 'crm/workflow_form.html', {'form': form, 'action': 'Create'})


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def rfm_analysis(request):
    """RFM Analysis dashboard"""
    if request.method == 'POST' and 'calculate_all' in request.POST:
        customers = Customer.objects.all()
        for customer in customers:
            calculate_rfm_scores(customer)
        messages.success(request, 'RFM scores calculated for all customers!')
        return redirect('rfm_analysis')
    
    rfm_scores = CustomerRFM.objects.all()
    segment_distribution = {}
    for rfm in rfm_scores:
        segment = rfm.rfm_segment or 'Uncategorized'
        segment_distribution[segment] = segment_distribution.get(segment, 0) + 1
    
    top_customers = rfm_scores.order_by('-recency_score', '-frequency_score', '-monetary_score')[:20]
    
    return render(request, 'crm/rfm_analysis.html', {
        'segment_distribution': segment_distribution,
        'top_customers': top_customers,
    })


@staff_login_required
@user_passes_test(lambda u: u.is_staff)
def cart_abandonment_list(request):
    """List abandoned carts"""
    abandoned_carts = CartAbandonment.objects.filter(recovered=False).order_by('-abandoned_at')
    
    page = request.GET.get('page', 1)
    paginator = Paginator(abandoned_carts, 20)
    try:
        abandoned_carts = paginator.page(page)
    except PageNotAnInteger:
        abandoned_carts = paginator.page(1)
    except EmptyPage:
        abandoned_carts = paginator.page(paginator.num_pages)
    
    total_value = sum([float(cart.total_value) for cart in abandoned_carts])
    
    return render(request, 'crm/cart_abandonment_list.html', {
        'abandoned_carts': abandoned_carts,
        'total_value': total_value,
    })
