
# FILE 1: crm/forms.py - COMPLETE CODE
# ============================================

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Customer, Order, Interaction, Task, Deal, Quote, Product,
    CustomerSegment, MarketingCampaign, LoyaltyProgram, SupportTicket, TicketMessage,
    CustomerFeedback, AutomationWorkflow, CommunicationPreference
)


class CustomerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    company_name = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control'})}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class StaffRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control'})}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        if commit:
            user.save()
        return user


class EmployeeForm(forms.ModelForm):
    """Form for creating/editing employees"""
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Required when creating new employee. Leave blank when editing to keep existing password."
    )
    
    class Meta:
        from .models import Employee
        model = Employee
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name', 'phone',
            'department', 'role', 'position', 'status',
            'hire_date', 'manager', 'reports_to',
            'address', 'city', 'state', 'country', 'postal_code',
            'bio', 'notes', 'profile_image',
            'can_view_customers', 'can_edit_customers',
            'can_view_orders', 'can_edit_orders',
            'can_view_products', 'can_edit_products',
            'can_view_reports', 'can_manage_tasks',
            'can_manage_tickets', 'can_view_analytics'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
            'reports_to': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        
        # Pre-fill username and email from user if editing
        if instance and instance.user:
            self.fields['username'].initial = instance.user.username
            self.fields['email'].initial = instance.user.email
            self.fields['username'].widget.attrs['readonly'] = True
            self.fields['password'].required = False
        else:
            # When creating, password is optional (will be auto-generated if not provided)
            self.fields['password'].required = False
        
        # Filter managers to only show employees
        from .models import Employee
        self.fields['manager'].queryset = Employee.objects.filter(status='active')
        self.fields['reports_to'].queryset = User.objects.filter(is_staff=True)
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        instance = self.instance
        
        if instance and instance.user:
            # If editing, allow same username
            if User.objects.filter(username=username).exclude(pk=instance.user.pk).exists():
                raise forms.ValidationError("A user with this username already exists.")
        else:
            # If creating, check if username exists
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("A user with this username already exists.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        instance = self.instance
        if instance and instance.user:
            # If editing, allow same email
            if User.objects.filter(email=email).exclude(pk=instance.user.pk).exists():
                raise forms.ValidationError("A user with this email already exists.")
        else:
            # If creating, check if email exists
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        from .models import Employee
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        employee = super().save(commit=False)
        
        # Auto-generate employee_id if not set (should always be the case now)
        if not employee.employee_id:
            # This will be handled by the model's save method, but we ensure it's empty
            pass
        
        if employee.pk:  # Editing existing employee
            user = employee.user
            user.email = self.cleaned_data['email']
            if self.cleaned_data.get('password'):
                user.set_password(self.cleaned_data['password'])
            user.save()
        else:  # Creating new employee
            username = self.cleaned_data['username']
            email = self.cleaned_data['email']
            password = self.cleaned_data.get('password') or User.objects.make_random_password()
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                is_staff=True,
                is_superuser=False  # Employees are not superusers
            )
            employee.user = user
            # Don't set employee_id - let the model's save() method auto-generate it
        
        if commit:
            employee.save()
        return employee


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'state', 'country', 
                  'postal_code', 'customer_type', 'company_name', 'industry', 'website', 'status', 
                  'source', 'assigned_to', 'next_follow_up', 'notes', 'tags', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_type': forms.Select(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'next_follow_up': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
        }
    profile_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'order_number', 'status', 'payment_status', 'subtotal', 'tax', 
                  'discount', 'shipping_cost', 'shipping_address', 'tracking_number', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'order_number': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'payment_status': forms.Select(attrs={'class': 'form-control'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'shipping_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'shipping_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tracking_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class InteractionForm(forms.ModelForm):
    class Meta:
        model = Interaction
        fields = ['interaction_type', 'subject', 'description', 'outcome', 'next_action']
        widgets = {
            'interaction_type': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'outcome': forms.TextInput(attrs={'class': 'form-control'}),
            'next_action': forms.TextInput(attrs={'class': 'form-control'}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'customer', 'assigned_to', 'priority', 'status', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = ['title', 'customer', 'amount', 'stage', 'probability', 'expected_close_date', 'description', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stage': forms.Select(attrs={'class': 'form-control'}),
            'probability': forms.NumberInput(attrs={'class': 'form-control'}),
            'expected_close_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['quote_number', 'customer', 'deal', 'status', 'subtotal', 'tax', 'discount', 'valid_until', 'notes']
        widgets = {
            'quote_number': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'deal': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valid_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'sku', 'price', 'cost', 'stock_quantity', 'min_stock_level', 'category', 'is_active', 'image', 'image_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_stock_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Or provide an external image URL'}),
        }
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))


# ============================================
# ENHANCED CRM FEATURES FORMS
# ============================================

class CustomerSegmentForm(forms.ModelForm):
    class Meta:
        model = CustomerSegment
        fields = ['name', 'description', 'criteria', 'is_dynamic']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'criteria': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'JSON format: {"status": "active", "total_spent__gte": 1000}'}),
            'is_dynamic': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MarketingCampaignForm(forms.ModelForm):
    class Meta:
        model = MarketingCampaign
        fields = ['name', 'campaign_type', 'status', 'subject', 'content', 'target_segment', 'scheduled_time']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'campaign_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'target_segment': forms.Select(attrs={'class': 'form-control'}),
            'scheduled_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['customer', 'subject', 'description', 'priority', 'status', 'source', 'category', 'assigned_to']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }


class TicketMessageForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ['message', 'is_internal']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_internal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CustomerFeedbackForm(forms.ModelForm):
    class Meta:
        model = CustomerFeedback
        fields = ['feedback_type', 'rating', 'comment', 'order', 'product', 'is_public']
        widgets = {
            'feedback_type': forms.Select(attrs={'class': 'form-control'}),
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'order': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AutomationWorkflowForm(forms.ModelForm):
    class Meta:
        model = AutomationWorkflow
        fields = ['name', 'description', 'trigger_type', 'trigger_conditions', 'action_type', 'action_config', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'trigger_type': forms.Select(attrs={'class': 'form-control'}),
            'trigger_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'JSON format'}),
            'action_type': forms.Select(attrs={'class': 'form-control'}),
            'action_config': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'JSON format'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CommunicationPreferenceForm(forms.ModelForm):
    class Meta:
        model = CommunicationPreference
        fields = ['email_enabled', 'sms_enabled', 'phone_enabled', 'push_notifications', 
                  'marketing_emails', 'language', 'timezone', 'preferred_contact_time', 
                  'gdpr_consent', 'data_processing_consent']
        widgets = {
            'email_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'phone_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'push_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'marketing_emails': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'timezone': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_contact_time': forms.TextInput(attrs={'class': 'form-control'}),
            'gdpr_consent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'data_processing_consent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

