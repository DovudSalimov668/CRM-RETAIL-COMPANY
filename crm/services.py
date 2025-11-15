# ============================================
# CRM SERVICES - Business Logic
# ============================================

from django.utils import timezone
from django.db.models import Sum, Count, Avg, Max, Min, Q
from datetime import datetime, timedelta
from decimal import Decimal
from .models import (
    Customer, Order, CustomerRFM, CustomerAnalytics, 
    AutomationWorkflow, CartAbandonment, LoyaltyProgram, LoyaltyTransaction
)


def calculate_rfm_scores(customer):
    """Calculate RFM (Recency, Frequency, Monetary) scores for a customer"""
    from .models import CustomerRFM
    
    now = timezone.now()
    
    # Recency: Days since last purchase
    last_order = customer.orders.order_by('-created_at').first()
    if last_order:
        days_since = (now - last_order.created_at).days
    else:
        days_since = 999  # No orders
    
    # Recency Score (1-5, lower days = higher score)
    if days_since <= 30:
        recency_score = 5
    elif days_since <= 60:
        recency_score = 4
    elif days_since <= 90:
        recency_score = 3
    elif days_since <= 180:
        recency_score = 2
    else:
        recency_score = 1
    
    # Frequency: Number of orders in last year
    one_year_ago = now - timedelta(days=365)
    order_count = customer.orders.filter(created_at__gte=one_year_ago).count()
    
    # Frequency Score (1-5)
    if order_count >= 20:
        frequency_score = 5
    elif order_count >= 10:
        frequency_score = 4
    elif order_count >= 5:
        frequency_score = 3
    elif order_count >= 2:
        frequency_score = 2
    else:
        frequency_score = 1
    
    # Monetary: Total spent in last year
    total_spent = customer.orders.filter(created_at__gte=one_year_ago).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Monetary Score (1-5)
    if total_spent >= 5000:
        monetary_score = 5
    elif total_spent >= 2000:
        monetary_score = 4
    elif total_spent >= 1000:
        monetary_score = 3
    elif total_spent >= 500:
        monetary_score = 2
    else:
        monetary_score = 1
    
    # Determine RFM Segment
    rfm_segment = determine_rfm_segment(recency_score, frequency_score, monetary_score)
    
    # Create or update RFM record
    rfm, created = CustomerRFM.objects.get_or_create(customer=customer)
    rfm.recency_score = recency_score
    rfm.frequency_score = frequency_score
    rfm.monetary_score = monetary_score
    rfm.rfm_segment = rfm_segment
    rfm.save()
    
    return rfm


def determine_rfm_segment(recency, frequency, monetary):
    """Determine customer segment based on RFM scores"""
    if recency >= 4 and frequency >= 4 and monetary >= 4:
        return "Champions"
    elif recency >= 3 and frequency >= 3 and monetary >= 3:
        return "Loyal Customers"
    elif recency >= 4 and frequency <= 2:
        return "Potential Loyalists"
    elif recency >= 3 and frequency <= 2:
        return "New Customers"
    elif recency <= 2 and frequency >= 3:
        return "At Risk"
    elif recency <= 2 and frequency <= 2:
        return "Lost"
    elif recency >= 3 and monetary <= 2:
        return "Hibernating"
    else:
        return "Need Attention"


def calculate_customer_analytics(customer):
    """Calculate advanced customer analytics"""
    from .models import CustomerAnalytics
    
    now = timezone.now()
    
    # Lifetime Value
    lifetime_value = customer.get_total_spent()
    
    # Average Order Value
    order_count = customer.orders.count()
    if order_count > 0:
        average_order_value = lifetime_value / order_count
    else:
        average_order_value = 0
    
    # Purchase Frequency (orders per year)
    if customer.date_joined:
        days_active = (now - customer.date_joined).days
        if days_active > 0:
            purchase_frequency = (order_count / days_active) * 365
        else:
            purchase_frequency = 0
    else:
        purchase_frequency = 0
    
    # Days since last purchase
    last_order = customer.orders.order_by('-created_at').first()
    if last_order:
        days_since_last_purchase = (now - last_order.created_at).days
    else:
        days_since_last_purchase = 999
    
    # Churn Probability (simple heuristic)
    if days_since_last_purchase > 180:
        churn_probability = 80
    elif days_since_last_purchase > 90:
        churn_probability = 50
    elif days_since_last_purchase > 60:
        churn_probability = 30
    elif days_since_last_purchase > 30:
        churn_probability = 15
    else:
        churn_probability = 5
    
    # Predicted next purchase (simple: average days between orders)
    if order_count > 1:
        orders = customer.orders.order_by('created_at')
        total_days = 0
        for i in range(1, order_count):
            days_between = (orders[i].created_at - orders[i-1].created_at).days
            total_days += days_between
        avg_days_between = total_days / (order_count - 1)
        predicted_date = now + timedelta(days=int(avg_days_between))
    else:
        predicted_date = None
    
    # Create or update analytics record
    analytics, created = CustomerAnalytics.objects.get_or_create(customer=customer)
    analytics.lifetime_value = Decimal(str(lifetime_value))
    analytics.average_order_value = Decimal(str(average_order_value))
    analytics.purchase_frequency = Decimal(str(purchase_frequency))
    analytics.days_since_last_purchase = days_since_last_purchase
    analytics.churn_probability = Decimal(str(churn_probability))
    analytics.predicted_next_purchase_date = predicted_date.date() if predicted_date else None
    analytics.save()
    
    return analytics


def execute_automation_workflow(trigger_type, customer=None, order=None, **kwargs):
    """Execute automation workflows based on trigger"""
    workflows = AutomationWorkflow.objects.filter(
        trigger_type=trigger_type,
        is_active=True
    )
    
    for workflow in workflows:
        # Check trigger conditions
        if check_trigger_conditions(workflow, customer, order, **kwargs):
            execute_workflow_action(workflow, customer, order, **kwargs)
            workflow.execution_count += 1
            workflow.last_executed = timezone.now()
            workflow.save()


def check_trigger_conditions(workflow, customer=None, order=None, **kwargs):
    """Check if workflow trigger conditions are met"""
    conditions = workflow.trigger_conditions or {}
    
    if not conditions:
        return True
    
    # Example condition checks
    if customer and 'status' in conditions:
        if customer.status != conditions['status']:
            return False
    
    if order and 'total_amount__gte' in conditions:
        if order.total_amount < Decimal(str(conditions['total_amount__gte'])):
            return False
    
    return True


def execute_workflow_action(workflow, customer=None, order=None, **kwargs):
    """Execute the workflow action"""
    config = workflow.action_config or {}
    
    if workflow.action_type == 'send_email':
        # Placeholder for email sending
        # In production, integrate with email service (SendGrid, Mailchimp, etc.)
        pass
    
    elif workflow.action_type == 'send_sms':
        # Placeholder for SMS sending
        # In production, integrate with SMS service (Twilio, etc.)
        pass
    
    elif workflow.action_type == 'create_task':
        from .models import Task
        Task.objects.create(
            title=config.get('title', 'Automated Task'),
            description=config.get('description', ''),
            customer=customer,
            assigned_to=workflow.created_by if workflow.created_by else None,
            priority=config.get('priority', 'medium'),
            due_date=timezone.now() + timedelta(days=config.get('due_days', 7))
        )
    
    elif workflow.action_type == 'award_points':
        if customer:
            loyalty, created = LoyaltyProgram.objects.get_or_create(customer=customer)
            points = config.get('points', 0)
            loyalty.points_balance += points
            loyalty.lifetime_points += points
            loyalty.save()
            
            LoyaltyTransaction.objects.create(
                loyalty_program=loyalty,
                transaction_type='earned',
                points=points,
                description=config.get('description', 'Automated points award'),
                order=order
            )
    
    elif workflow.action_type == 'update_customer_status':
        if customer and 'status' in config:
            customer.status = config['status']
            customer.save()


def track_cart_abandonment(customer, cart_data, total_value):
    """Track abandoned shopping cart"""
    CartAbandonment.objects.create(
        customer=customer,
        cart_data=cart_data,
        total_value=total_value
    )


def award_loyalty_points(customer, order, points_per_dollar=1):
    """Award loyalty points for an order"""
    if order and order.payment_status == 'paid':
        loyalty, created = LoyaltyProgram.objects.get_or_create(customer=customer)
        points = int(float(order.total_amount) * points_per_dollar)
        
        loyalty.points_balance += points
        loyalty.lifetime_points += points
        loyalty.save()
        
        LoyaltyTransaction.objects.create(
            loyalty_program=loyalty,
            transaction_type='earned',
            points=points,
            description=f'Points earned from order {order.order_number}',
            order=order
        )
        
        # Update tier based on lifetime points
        update_loyalty_tier(loyalty)
        
        return points
    return 0


def update_loyalty_tier(loyalty):
    """Update customer loyalty tier based on lifetime points"""
    if loyalty.lifetime_points >= 10000:
        loyalty.tier = 'platinum'
    elif loyalty.lifetime_points >= 5000:
        loyalty.tier = 'gold'
    elif loyalty.lifetime_points >= 2000:
        loyalty.tier = 'silver'
    else:
        loyalty.tier = 'bronze'
    loyalty.save()

