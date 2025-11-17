# FILE: crm/admin.py
# COMPLETE ADMIN CONFIGURATION

from django.contrib import admin
from .models import (
    Customer, Product, Order, OrderItem, Interaction, Task, Deal, Quote,
    CustomerSegment, CustomerRFM, CommunicationPreference, MarketingCampaign,
    LoyaltyProgram, LoyaltyTransaction, SupportTicket, TicketMessage,
    CustomerFeedback, AutomationWorkflow, CartAbandonment, CustomerAnalytics,
    Employee
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone', 'status', 'source', 'assigned_to', 'date_joined']
    list_filter = ['status', 'source', 'customer_type', 'date_joined', 'assigned_to']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'company_name']
    list_editable = ['status']
    date_hierarchy = 'date_joined'
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Business Details', {
            'fields': ('customer_type', 'company_name', 'industry', 'website')
        }),
        ('CRM Details', {
            'fields': ('status', 'source', 'assigned_to', 'next_follow_up')
        }),
        ('Additional Info', {
            'fields': ('notes', 'tags')
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'cost', 'stock_quantity', 'min_stock_level', 'category', 'is_active', 'profit_margin']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'sku', 'description']
    list_editable = ['price', 'stock_quantity', 'is_active']
    
    def profit_margin(self, obj):
        return f"{obj.get_profit_margin():.2f}%"
    profit_margin.short_description = 'Profit %'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'discount', 'subtotal']
    readonly_fields = ['subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'payment_status', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'customer__first_name', 'customer__last_name', 'customer__email']
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status', 'payment_status')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax', 'discount', 'shipping_cost', 'total_amount')
        }),
        ('Shipping', {
            'fields': ('shipping_address', 'tracking_number', 'shipped_date', 'delivered_date')
        }),
        ('Additional', {
            'fields': ('notes', 'created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'interaction_type', 'subject', 'created_at', 'created_by']
    list_filter = ['interaction_type', 'created_at']
    search_fields = ['customer__first_name', 'customer__last_name', 'subject', 'description']
    date_hierarchy = 'created_at'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'customer', 'assigned_to', 'priority', 'status', 'due_date', 'overdue']
    list_filter = ['status', 'priority', 'due_date', 'assigned_to']
    search_fields = ['title', 'description', 'customer__first_name', 'customer__last_name']
    list_editable = ['status', 'priority']
    date_hierarchy = 'due_date'
    
    def overdue(self, obj):
        return "⚠️ Yes" if obj.is_overdue() else "✅ No"
    overdue.short_description = 'Overdue'


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ['title', 'customer', 'amount', 'stage', 'probability', 'weighted_value', 'expected_close_date', 'assigned_to']
    list_filter = ['stage', 'expected_close_date', 'assigned_to']
    search_fields = ['title', 'description', 'customer__first_name', 'customer__last_name']
    list_editable = ['stage', 'probability']
    date_hierarchy = 'expected_close_date'
    
    def weighted_value(self, obj):
        return f"${obj.get_weighted_value():.2f}"
    weighted_value.short_description = 'Weighted Value'


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['quote_number', 'customer', 'status', 'total_amount', 'valid_until', 'created_at', 'expired']
    list_filter = ['status', 'created_at', 'valid_until']
    search_fields = ['quote_number', 'customer__first_name', 'customer__last_name']
    date_hierarchy = 'created_at'
    readonly_fields = ['total_amount', 'created_at']
    
    def expired(self, obj):
        return "⚠️ Expired" if obj.is_expired() else "✅ Valid"
    expired.short_description = 'Status'


# ============================================
# ENHANCED CRM FEATURES ADMIN
# ============================================

@admin.register(CustomerSegment)
class CustomerSegmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_dynamic', 'customer_count', 'created_at']
    list_filter = ['is_dynamic', 'created_at']
    search_fields = ['name', 'description']


@admin.register(CustomerRFM)
class CustomerRFMAdmin(admin.ModelAdmin):
    list_display = ['customer', 'recency_score', 'frequency_score', 'monetary_score', 'rfm_segment', 'last_calculated']
    list_filter = ['rfm_segment', 'last_calculated']
    search_fields = ['customer__first_name', 'customer__last_name', 'customer__email']


@admin.register(CommunicationPreference)
class CommunicationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['customer', 'email_enabled', 'sms_enabled', 'marketing_emails', 'gdpr_consent']
    list_filter = ['email_enabled', 'sms_enabled', 'marketing_emails', 'gdpr_consent']
    search_fields = ['customer__first_name', 'customer__last_name', 'customer__email']


@admin.register(MarketingCampaign)
class MarketingCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'campaign_type', 'status', 'sent_count', 'opened_count', 'clicked_count', 'open_rate', 'created_at']
    list_filter = ['campaign_type', 'status', 'created_at']
    search_fields = ['name', 'subject', 'content']
    readonly_fields = ['sent_count', 'opened_count', 'clicked_count', 'conversion_count', 'sent_at']
    
    def open_rate(self, obj):
        return f"{obj.get_open_rate():.2f}%"
    open_rate.short_description = 'Open Rate'


@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ['customer', 'tier', 'points_balance', 'lifetime_points', 'total_redeemed', 'join_date']
    list_filter = ['tier', 'join_date']
    search_fields = ['customer__first_name', 'customer__last_name', 'customer__email']


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ['loyalty_program', 'transaction_type', 'points', 'description', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['description', 'loyalty_program__customer__first_name']


class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 1
    fields = ['message', 'is_internal', 'created_by', 'created_at']
    readonly_fields = ['created_at']


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'customer', 'subject', 'priority', 'status', 'source', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'source', 'created_at', 'assigned_to']
    search_fields = ['ticket_number', 'subject', 'description', 'customer__first_name', 'customer__last_name']
    inlines = [TicketMessageInline]
    readonly_fields = ['ticket_number', 'created_at', 'updated_at']


@admin.register(CustomerFeedback)
class CustomerFeedbackAdmin(admin.ModelAdmin):
    list_display = ['customer', 'feedback_type', 'rating', 'sentiment', 'is_public', 'responded', 'created_at']
    list_filter = ['feedback_type', 'rating', 'sentiment', 'is_public', 'responded', 'created_at']
    search_fields = ['comment', 'customer__first_name', 'customer__last_name']
    list_editable = ['responded']


@admin.register(AutomationWorkflow)
class AutomationWorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'trigger_type', 'action_type', 'is_active', 'execution_count', 'last_executed']
    list_filter = ['trigger_type', 'action_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']


@admin.register(CartAbandonment)
class CartAbandonmentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'total_value', 'abandoned_at', 'recovered', 'reminder_sent']
    list_filter = ['recovered', 'reminder_sent', 'abandoned_at']
    search_fields = ['customer__first_name', 'customer__last_name', 'customer__email']
    date_hierarchy = 'abandoned_at'


@admin.register(CustomerAnalytics)
class CustomerAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['customer', 'lifetime_value', 'average_order_value', 'purchase_frequency', 'churn_probability', 'last_calculated']
    list_filter = ['last_calculated']
    search_fields = ['customer__first_name', 'customer__last_name', 'customer__email']
    readonly_fields = ['last_calculated']


from .models import OTPCode

@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ['email', 'code', 'user', 'created_at', 'expires_at', 'is_used', 'is_expired']
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['email', 'code']
    readonly_fields = ['created_at', 'expires_at']
    ordering = ['-created_at']
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'first_name', 'last_name', 'email', 'department', 'role', 'status', 'hire_date', 'has_user']
    list_filter = ['department', 'role', 'status', 'hire_date']
    search_fields = ['employee_id', 'first_name', 'last_name', 'email', 'position']
    list_editable = ['status']
    date_hierarchy = 'hire_date'
    fieldsets = (
        ('User Account', {
            'fields': ('user', 'username', 'password', 'user_is_staff', 'user_is_superuser'),
            'description': 'Option 1: Select existing user. Option 2: Leave user blank and provide username (password optional - will be auto-generated if blank).'
        }),
        ('Basic Information', {
            'fields': ('employee_id', 'first_name', 'last_name', 'email', 'phone', 'profile_image'),
            'description': 'Employee ID will be automatically generated when creating (format: EMP-0001, EMP-0002, etc.)'
        }),
        ('Employment Details', {
            'fields': ('department', 'role', 'position', 'status', 'hire_date', 'termination_date')
        }),
        ('Reporting Structure', {
            'fields': ('manager', 'reports_to'),
            'description': 'Select a manager from existing employees. You can create employees first, then assign managers later.'
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Additional Info', {
            'fields': ('bio', 'notes')
        }),
        ('Permissions', {
            'fields': (
                'can_view_customers', 'can_edit_customers',
                'can_view_orders', 'can_edit_orders',
                'can_view_products', 'can_edit_products',
                'can_view_reports', 'can_manage_tasks',
                'can_manage_tickets', 'can_view_analytics'
            )
        }),
    )
    
    def has_user(self, obj):
        return "✅ Yes" if obj.user else "❌ No"
    has_user.short_description = 'Has User'
    
    def get_form(self, request, obj=None, **kwargs):
        from django import forms
        from .models import Employee
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Add username and password fields for creating new users
        if obj is None:  # Creating new employee
            class EmployeeAdminForm(forms.ModelForm):
                username = forms.CharField(
                    required=False,
                    help_text="Required if creating new user account. Leave blank if linking to existing user."
                )
                password = forms.CharField(
                    required=False,
                    widget=forms.PasswordInput,
                    help_text="Optional. Leave blank to auto-generate a secure random password."
                )
                user_is_staff = forms.BooleanField(
                    required=False,
                    initial=True,
                    help_text="Allow user to access admin interface. Usually checked for employees."
                )
                user_is_superuser = forms.BooleanField(
                    required=False,
                    initial=False,
                    help_text="Give user full admin access. Usually unchecked for regular employees."
                )
                
                class Meta:
                    model = Employee
                    fields = '__all__'
                
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    # Make employee_id optional and hidden when creating (will be auto-generated)
                    if not self.instance.pk:
                        if 'employee_id' in self.fields:
                            self.fields['employee_id'].required = False
                            self.fields['employee_id'].widget = forms.HiddenInput()
                            self.fields['employee_id'].help_text = "Will be auto-generated"
                        # Make user field optional when creating
                        self.fields['user'].required = False
                        self.fields['user'].help_text = "Select existing user or create new one below"
                    # Filter managers to show all employees
                    if 'manager' in self.fields:
                        self.fields['manager'].queryset = Employee.objects.all()
                    # Make email required
                    if 'email' in self.fields:
                        self.fields['email'].required = True
                
                def clean_username(self):
                    username = self.cleaned_data.get('username')
                    if username:
                        if User.objects.filter(username=username).exists():
                            raise forms.ValidationError("A user with this username already exists.")
                    return username
                
                def clean_email(self):
                    email = self.cleaned_data.get('email')
                    if email:
                        # Check if email is already used by another user
                        if User.objects.filter(email=email).exists():
                            raise forms.ValidationError("A user with this email already exists.")
                        # Check if email is already used by another employee
                        if Employee.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
                            raise forms.ValidationError("An employee with this email already exists.")
                    return email
                
                def clean(self):
                    cleaned_data = super().clean()
                    user = cleaned_data.get('user')
                    username = cleaned_data.get('username')
                    
                    # If creating new employee without user
                    if not self.instance.pk:
                        if not user and not username:
                            raise forms.ValidationError("Either select an existing user or provide username to create new user account.")
                    
                    return cleaned_data
                
                def save(self, commit=True):
                    employee = super().save(commit=False)
                    username = self.cleaned_data.get('username')
                    password = self.cleaned_data.get('password')
                    is_staff = self.cleaned_data.get('user_is_staff', True)
                    is_superuser = self.cleaned_data.get('user_is_superuser', False)
                    
                    # Create user if username provided (password optional - will be auto-generated)
                    if username and not employee.user:
                        # Auto-generate password if not provided
                        if not password:
                            password = User.objects.make_random_password()
                        
                        user = User.objects.create_user(
                            username=username,
                            email=employee.email,
                            password=password,
                            first_name=employee.first_name,
                            last_name=employee.last_name,
                            is_staff=is_staff,
                            is_superuser=is_superuser
                        )
                        employee.user = user
                    
                    # Ensure employee_id is empty so model's save() will auto-generate it
                    # CharField with blank=True accepts empty string, which triggers auto-generation
                    if not employee.employee_id or (isinstance(employee.employee_id, str) and employee.employee_id.strip() == ''):
                        employee.employee_id = ''
                    
                    if commit:
                        employee.save()
                    return employee
            
            return EmployeeAdminForm
        else:  # Editing existing employee
            class EmployeeEditForm(forms.ModelForm):
                class Meta:
                    model = Employee
                    fields = '__all__'
                
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    # Make employee_id read-only when editing
                    if 'employee_id' in self.fields:
                        self.fields['employee_id'].widget.attrs['readonly'] = True
                        self.fields['employee_id'].help_text = "Employee ID cannot be changed after creation."
                    # When editing, allow selecting any employee as manager except self
                    if 'manager' in self.fields:
                        self.fields['manager'].queryset = Employee.objects.exclude(pk=obj.pk)
            
            return EmployeeEditForm
