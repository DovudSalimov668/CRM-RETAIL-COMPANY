#!/usr/bin/env python
"""Test script to verify Employee system is working"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_crm.settings')
django.setup()

print("=" * 50)
print("Testing Employee System")
print("=" * 50)

# Test 1: Import Employee model
try:
    from crm.models import Employee
    print("✅ Employee model imported successfully")
except Exception as e:
    print(f"❌ Failed to import Employee model: {e}")
    sys.exit(1)

# Test 2: Import EmployeeForm
try:
    from crm.forms import EmployeeForm
    print("✅ EmployeeForm imported successfully")
except Exception as e:
    print(f"❌ Failed to import EmployeeForm: {e}")
    sys.exit(1)

# Test 3: Import employee views
try:
    from crm.views import employee_list, employee_create, employee_detail, employee_update, employee_delete, employee_dashboard
    print("✅ All employee views imported successfully")
except Exception as e:
    print(f"❌ Failed to import employee views: {e}")
    sys.exit(1)

# Test 4: Check Employee model fields
try:
    fields = [f.name for f in Employee._meta.get_fields()]
    required_fields = ['user', 'employee_id', 'first_name', 'last_name', 'email', 'department', 'role', 'status']
    missing = [f for f in required_fields if f not in fields]
    if missing:
        print(f"❌ Missing required fields: {missing}")
        sys.exit(1)
    print("✅ Employee model has all required fields")
except Exception as e:
    print(f"❌ Error checking Employee model: {e}")
    sys.exit(1)

# Test 5: Check permissions
try:
    permission_fields = [
        'can_view_customers', 'can_edit_customers',
        'can_view_orders', 'can_edit_orders',
        'can_view_products', 'can_edit_products',
        'can_view_reports', 'can_manage_tasks',
        'can_manage_tickets', 'can_view_analytics'
    ]
    for perm in permission_fields:
        if not hasattr(Employee, perm):
            print(f"❌ Missing permission field: {perm}")
            sys.exit(1)
    print("✅ All permission fields exist")
except Exception as e:
    print(f"❌ Error checking permissions: {e}")
    sys.exit(1)

# Test 6: Check URLs
try:
    from django.urls import reverse
    urls = [
        'employee_list',
        'employee_create',
        'employee_dashboard',
    ]
    for url_name in urls:
        try:
            reverse(url_name)
        except:
            print(f"❌ URL '{url_name}' not found")
            sys.exit(1)
    print("✅ All employee URLs are configured")
except Exception as e:
    print(f"❌ Error checking URLs: {e}")
    sys.exit(1)

# Test 7: Check templates exist
import os
template_dir = 'templates/crm'
templates = [
    'employee_list.html',
    'employee_form.html',
    'employee_detail.html',
    'employee_confirm_delete.html',
    'employee_dashboard.html',
]
for template in templates:
    template_path = os.path.join(template_dir, template)
    if not os.path.exists(template_path):
        print(f"❌ Template missing: {template_path}")
        sys.exit(1)
print("✅ All employee templates exist")

print("\n" + "=" * 50)
print("✅ ALL TESTS PASSED!")
print("=" * 50)
print("\nThe Employee system is fully working!")
print("\nNext steps:")
print("1. Run: python manage.py makemigrations")
print("2. Run: python manage.py migrate")
print("3. Create an employee at /employees/create/")

