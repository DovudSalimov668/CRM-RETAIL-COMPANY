#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_crm.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
# In Django shell


import os
print("BREVO_API_KEY:", os.getenv('BREVO_API_KEY')[:20] + "..." if os.getenv('BREVO_API_KEY') else "NOT SET")
print("BREVO_SENDER_EMAIL:", os.getenv('BREVO_SENDER_EMAIL'))
print("BREVO_SENDER_NAME:", os.getenv('BREVO_SENDER_NAME'))