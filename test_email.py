"""
Quick test script to verify Brevo email configuration
Run: python test_email.py
"""
import os
import sys
import django

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_crm.settings')
django.setup()

from django.conf import settings
from crm.email_utils import send_email_via_brevo

def test_email_config():
    """Test email configuration"""
    print("=" * 60)
    print("📧 Testing Brevo Email Configuration")
    print("=" * 60)
    
    # Check API Key
    api_key = os.environ.get('BREVO_API_KEY') or getattr(settings, 'BREVO_API_KEY', None)
    print(f"\n1. API Key Status:")
    if api_key:
        print(f"   ✅ API Key found (length: {len(api_key)})")
        print(f"   🔒 First 10 chars: {api_key[:10]}...")
    else:
        print("   ❌ API Key NOT FOUND")
        print("   💡 Set BREVO_API_KEY in .env file or environment variables")
        return False
    
    # Check Sender Email
    sender_email = getattr(settings, 'BREVO_SENDER_EMAIL', 'ggvpby6996@gmail.com')
    sender_name = getattr(settings, 'BREVO_SENDER_NAME', 'Retail CRM System')
    print(f"\n2. Sender Configuration:")
    print(f"   📧 Email: {sender_email}")
    print(f"   👤 Name: {sender_name}")
    print(f"   ⚠️  Make sure '{sender_email}' is verified in Brevo dashboard!")
    
    # Test email sending (optional - uncomment to actually send)
    print(f"\n3. Test Email Sending:")
    test_recipient = input("   Enter test email address (or press Enter to skip): ").strip()
    
    if test_recipient:
        print(f"\n   📤 Sending test email to {test_recipient}...")
        result = send_email_via_brevo(
            subject="Test Email from Retail CRM",
            html_content="<h1>Test Email</h1><p>If you receive this, email sending is working correctly!</p>",
            text_content="Test Email\n\nIf you receive this, email sending is working correctly!",
            recipients=[test_recipient]
        )
        
        if result:
            print(f"\n   ✅ Test email sent successfully!")
            print(f"   📬 Check inbox and spam folder for: {test_recipient}")
            print(f"   ⏱️  Delivery may take 1-5 minutes")
        else:
            print(f"\n   ❌ Failed to send test email")
            print(f"   💡 Check the error messages above")
    else:
        print("   ⏭️  Skipped (no email address provided)")
    
    print("\n" + "=" * 60)
    print("📋 Troubleshooting Checklist:")
    print("=" * 60)
    print("1. ✅ API Key is configured")
    print("2. ⚠️  Verify sender email in Brevo:")
    print(f"   → Go to: https://app.brevo.com/settings/senders")
    print(f"   → Add/verify: {sender_email}")
    print("3. 📬 Check spam/junk folder")
    print("4. ⏱️  Wait 1-5 minutes for delivery")
    print("5. 🔍 Check Brevo dashboard for sending logs:")
    print("   → https://app.brevo.com/statistics/email")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        test_email_config()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

