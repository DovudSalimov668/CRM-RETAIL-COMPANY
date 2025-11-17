# FILE: crm/models.py
# COMPLETE ENHANCED VERSION - COPY THIS ENTIRE FILE
# Location: C:\Users\User\Desktop\CRM\crm\models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from datetime import timedelta


class Customer(models.Model):
    """Enhanced Customer model with all CRM features"""
    
    CUSTOMER_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('business', 'Business'),
    ]
    
    STATUS_CHOICES = [
        ('lead', 'Lead'),
        ('prospect', 'Prospect'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('vip', 'VIP'),
    ]
    
    SOURCE_CHOICES = [
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('social_media', 'Social Media'),
        ('advertisement', 'Advertisement'),
        ('walk_in', 'Walk-in'),
        ('other', 'Other'),
    ]
    
    # Basic Information
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='customer_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    
    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Business Information
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES, default='individual')
    company_name = models.CharField(max_length=200, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    
    # CRM Fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='lead')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='website')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_customers')
    
    # Dates
    date_joined = models.DateTimeField(default=timezone.now)
    last_contact_date = models.DateTimeField(null=True, blank=True)
    next_follow_up = models.DateTimeField(null=True, blank=True)
    
    # Additional Info
    notes = models.TextField(blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    # Media
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='customers_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_total_orders(self):
        return self.orders.count()
    
    def get_total_spent(self):
        from django.db.models import Sum
        total = self.orders.aggregate(total=Sum('total_amount'))['total'] or 0
        return total
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Product(models.Model):
    """Enhanced Product model with inventory management"""
    
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('food', 'Food & Beverage'),
        ('books', 'Books'),
        ('home', 'Home & Garden'),
        ('sports', 'Sports'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    min_stock_level = models.IntegerField(default=10)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='other')
    is_active = models.BooleanField(default=True)
    image_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def is_low_stock(self):
        return self.stock_quantity <= self.min_stock_level
    
    def get_profit_margin(self):
        if self.cost > 0:
            return ((self.price - self.cost) / self.price) * 100
        return 0


class Order(models.Model):
    """Enhanced Order model with payment and shipping tracking"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Shipping
    shipping_address = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    shipped_date = models.DateTimeField(null=True, blank=True)
    delivered_date = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def calculate_total(self):
        self.total_amount = self.subtotal + self.tax + self.shipping_cost - self.discount
        self.save()


class OrderItem(models.Model):
    """Order line items"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.subtotal = (self.quantity * self.unit_price) - self.discount
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Interaction(models.Model):
    """Customer interaction tracking"""
    
    INTERACTION_TYPE_CHOICES = [
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('note', 'Note'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    outcome = models.CharField(max_length=200, blank=True)
    next_action = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.interaction_type} - {self.subject}"


class Task(models.Model):
    """Task management for CRM activities"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tasks_created')
    
    class Meta:
        ordering = ['due_date', '-priority']
    
    def __str__(self):
        return self.title
    
    def is_overdue(self):
        if self.status != 'completed' and self.due_date < timezone.now():
            return True
        return False


class Deal(models.Model):
    """Sales pipeline and opportunity tracking"""
    
    STAGE_CHOICES = [
        ('lead', 'Lead'),
        ('qualified', 'Qualified'),
        ('proposal', 'Proposal'),
        ('negotiation', 'Negotiation'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
    ]
    
    title = models.CharField(max_length=200)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='deals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='lead')
    probability = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    expected_close_date = models.DateField()
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='deals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_weighted_value(self):
        return (self.amount * self.probability) / 100


class Quote(models.Model):
    """Quote/Proposal management"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    quote_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='quotes')
    deal = models.ForeignKey(Deal, on_delete=models.SET_NULL, null=True, blank=True, related_name='quotes')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valid_until = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Quote {self.quote_number}"
    
    def is_expired(self):
        from datetime import date
        return date.today() > self.valid_until and self.status not in ['accepted', 'rejected']


# ============================================
# ENHANCED CRM FEATURES - COMPLETE REQUIREMENTS
# ============================================

class CustomerSegment(models.Model):
    """Customer segmentation for targeted marketing"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    criteria = models.JSONField(default=dict, help_text="JSON criteria for segment membership")
    is_dynamic = models.BooleanField(default=True, help_text="Auto-update based on criteria")
    customer_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CustomerRFM(models.Model):
    """RFM Analysis scores for customers"""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='rfm_score')
    recency_score = models.IntegerField(default=0, help_text="1-5 score")
    frequency_score = models.IntegerField(default=0, help_text="1-5 score")
    monetary_score = models.IntegerField(default=0, help_text="1-5 score")
    rfm_segment = models.CharField(max_length=50, blank=True, help_text="e.g., Champions, Loyal, At Risk")
    last_calculated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer} - RFM: {self.recency_score}{self.frequency_score}{self.monetary_score}"


class CommunicationPreference(models.Model):
    """Customer communication preferences"""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='comm_preferences')
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    phone_enabled = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=False)
    marketing_emails = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    preferred_contact_time = models.CharField(max_length=50, blank=True)
    gdpr_consent = models.BooleanField(default=False)
    gdpr_consent_date = models.DateTimeField(null=True, blank=True)
    data_processing_consent = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Preferences for {self.customer}"


class MarketingCampaign(models.Model):
    """Marketing campaign management"""
    CAMPAIGN_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('social', 'Social Media'),
        ('multi', 'Multi-Channel'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=200)
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    subject = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    target_segment = models.ForeignKey(CustomerSegment, on_delete=models.SET_NULL, null=True, blank=True)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    sent_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    conversion_count = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_open_rate(self):
        if self.sent_count > 0:
            return (self.opened_count / self.sent_count) * 100
        return 0
    
    def get_click_rate(self):
        if self.sent_count > 0:
            return (self.clicked_count / self.sent_count) * 100
        return 0


class LoyaltyProgram(models.Model):
    """Loyalty and rewards program"""
    TIER_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]
    
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='loyalty')
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='bronze')
    points_balance = models.IntegerField(default=0)
    lifetime_points = models.IntegerField(default=0)
    total_redeemed = models.IntegerField(default=0)
    join_date = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer} - {self.tier} ({self.points_balance} pts)"


class LoyaltyTransaction(models.Model):
    """Loyalty points transactions"""
    TRANSACTION_TYPE_CHOICES = [
        ('earned', 'Points Earned'),
        ('redeemed', 'Points Redeemed'),
        ('expired', 'Points Expired'),
        ('adjusted', 'Manual Adjustment'),
    ]
    
    loyalty_program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    points = models.IntegerField()
    description = models.CharField(max_length=200)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_type} - {self.points} points"


class SupportTicket(models.Model):
    """Customer support ticket system"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting_customer', 'Waiting for Customer'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    SOURCE_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('chat', 'Live Chat'),
        ('social', 'Social Media'),
        ('in_store', 'In-Store'),
        ('web', 'Website'),
    ]
    
    ticket_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='tickets')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='web')
    category = models.CharField(max_length=100, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    first_response_time = models.DateTimeField(null=True, blank=True)
    resolution_time = models.DateTimeField(null=True, blank=True)
    sla_deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tickets_created')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Ticket #{self.ticket_number} - {self.subject}"


class TicketMessage(models.Model):
    """Messages/updates on support tickets"""
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField()
    is_internal = models.BooleanField(default=False, help_text="Internal note (not visible to customer)")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message on {self.ticket.ticket_number}"


class CustomerFeedback(models.Model):
    """Customer feedback and surveys"""
    FEEDBACK_TYPE_CHOICES = [
        ('nps', 'Net Promoter Score'),
        ('csat', 'Customer Satisfaction'),
        ('ces', 'Customer Effort Score'),
        ('review', 'Product Review'),
        ('general', 'General Feedback'),
    ]
    
    RATING_CHOICES = [
        (1, '1 - Very Poor'),
        (2, '2 - Poor'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES)
    rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    comment = models.TextField(blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    ticket = models.ForeignKey(SupportTicket, on_delete=models.SET_NULL, null=True, blank=True)
    sentiment = models.CharField(max_length=20, blank=True, help_text="Auto-detected: positive, negative, neutral")
    is_public = models.BooleanField(default=False, help_text="Show in public reviews")
    responded = models.BooleanField(default=False)
    response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.feedback_type} - {self.customer}"


class AutomationWorkflow(models.Model):
    """Marketing and sales automation workflows"""
    TRIGGER_TYPE_CHOICES = [
        ('customer_created', 'New Customer'),
        ('order_placed', 'Order Placed'),
        ('order_delivered', 'Order Delivered'),
        ('cart_abandoned', 'Cart Abandoned'),
        ('customer_inactive', 'Customer Inactive'),
        ('ticket_created', 'Support Ticket Created'),
        ('feedback_received', 'Feedback Received'),
        ('custom', 'Custom Trigger'),
    ]
    
    ACTION_TYPE_CHOICES = [
        ('send_email', 'Send Email'),
        ('send_sms', 'Send SMS'),
        ('create_task', 'Create Task'),
        ('assign_to_user', 'Assign to User'),
        ('update_customer_status', 'Update Customer Status'),
        ('add_to_segment', 'Add to Segment'),
        ('award_points', 'Award Loyalty Points'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_TYPE_CHOICES)
    trigger_conditions = models.JSONField(default=dict, help_text="Additional conditions for trigger")
    action_type = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES)
    action_config = models.JSONField(default=dict, help_text="Configuration for the action")
    is_active = models.BooleanField(default=True)
    execution_count = models.IntegerField(default=0)
    last_executed = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CartAbandonment(models.Model):
    """Track abandoned shopping carts"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='abandoned_carts')
    cart_data = models.JSONField(default=dict, help_text="Stored cart items")
    total_value = models.DecimalField(max_digits=10, decimal_places=2)
    abandoned_at = models.DateTimeField(auto_now_add=True)
    recovered = models.BooleanField(default=False)
    recovered_at = models.DateTimeField(null=True, blank=True)
    reminder_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-abandoned_at']
    
    def __str__(self):
        return f"Abandoned cart - {self.customer}"


class CustomerAnalytics(models.Model):
    """Stored customer analytics calculations"""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='analytics')
    lifetime_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchase_frequency = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    days_since_last_purchase = models.IntegerField(default=0)
    churn_probability = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="0-100 percentage")
    predicted_next_purchase_date = models.DateField(null=True, blank=True)
    last_calculated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analytics for {self.customer}"


class OTPCode(models.Model):
    """OTP code for email-based authentication"""
    email = models.EmailField()
    code = models.CharField(max_length=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'code', 'is_used']),
        ]
    
    def __str__(self):
        return f"OTP for {self.email}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at


class Employee(models.Model):
    """
    Employee model - for staff members who are not admins
    Employees have limited access compared to superusers
    """
    
    DEPARTMENT_CHOICES = [
        ('sales', 'Sales'),
        ('support', 'Customer Support'),
        ('marketing', 'Marketing'),
        ('operations', 'Operations'),
        ('finance', 'Finance'),
        ('hr', 'Human Resources'),
        ('it', 'IT'),
        ('other', 'Other'),
    ]
    
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('senior', 'Senior Employee'),
        ('employee', 'Employee'),
        ('intern', 'Intern'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
    ]
    
    # Link to User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile', null=True, blank=True)
    
    # Basic Information
    employee_id = models.CharField(max_length=50, unique=True, blank=True, help_text="Unique employee ID (auto-generated if not provided)")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Employment Details
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='other')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='employee')
    position = models.CharField(max_length=200, blank=True, help_text="Job title/position")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Employment Dates
    hire_date = models.DateField(default=timezone.now)
    termination_date = models.DateField(null=True, blank=True)
    
    # Manager/Reporting
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    reports_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='team_members')
    
    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Additional Info
    bio = models.TextField(blank=True, help_text="Employee bio/description")
    notes = models.TextField(blank=True, help_text="Internal notes")
    
    # Media
    profile_image = models.ImageField(upload_to='employees/', null=True, blank=True)
    
    # Permissions (what employees can access)
    can_view_customers = models.BooleanField(default=True)
    can_edit_customers = models.BooleanField(default=False)
    can_view_orders = models.BooleanField(default=True)
    can_edit_orders = models.BooleanField(default=False)
    can_view_products = models.BooleanField(default=True)
    can_edit_products = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=False)
    can_manage_tasks = models.BooleanField(default=True)
    can_manage_tickets = models.BooleanField(default=True)
    can_view_analytics = models.BooleanField(default=False)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='employees_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-hire_date']
        verbose_name_plural = 'Employees'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_active(self):
        return self.status == 'active'
    
    def save(self, *args, **kwargs):
        # Auto-generate employee_id if not provided
        if not self.employee_id or (isinstance(self.employee_id, str) and self.employee_id.strip() == ''):
            # Generate unique employee ID by finding the highest existing number
            # Query all employees with valid employee_id format
            existing_ids = Employee.objects.exclude(
                employee_id__isnull=True
            ).exclude(
                employee_id=''
            ).filter(
                employee_id__startswith='EMP-'
            ).values_list('employee_id', flat=True)
            
            max_num = 0
            for emp_id in existing_ids:
                try:
                    num = int(emp_id.split('-')[-1])
                    if num > max_num:
                        max_num = num
                except (ValueError, IndexError):
                    continue
            
            new_num = max_num + 1
            self.employee_id = f"EMP-{new_num:04d}"
        
        # Set user as staff if employee is created and user exists
        if hasattr(self, 'user') and self.user and not self.user.is_staff:
            self.user.is_staff = True
            self.user.save()
        
        super().save(*args, **kwargs)