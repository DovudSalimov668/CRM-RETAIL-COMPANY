"""
Test OTP email sending - verifies actual email delivery
Run: python test_otp_email.py
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

from crm.otp_service import send_otp_via_brevo

def test_otp_email():
    """Test OTP email sending"""
    print("=" * 60)
    print("Testing OTP Email Sending")
    print("=" * 60)
    
    test_email = input("\nEnter email address to test: ").strip()
    
    if not test_email:
        print("No email provided. Exiting.")
        return
    
    print(f"\nSending test OTP to {test_email}...")
    print("-" * 60)
    
    # Generate a test OTP
    test_otp = "123456"
    
    # Try to send
    result = send_otp_via_brevo(test_email, test_otp)
    
    print("-" * 60)
    
    if result:
        print(f"\n✅ SUCCESS: Email was sent to Brevo API")
        print(f"📧 Check inbox (and spam) for: {test_email}")
        print(f"🔑 Test OTP code: {test_otp}")
        print(f"\n⚠️  If email doesn't arrive:")
        print(f"   1. Check spam/junk folder")
        print(f"   2. Verify sender email in Brevo dashboard")
        print(f"   3. Wait 2-5 minutes for delivery")
        print(f"   4. Check: https://app.brevo.com/statistics/email")
    else:
        print(f"\n❌ FAILED: Email was NOT sent")
        print(f"💡 Check the error messages above")
        print(f"💡 Common issues:")
        print(f"   - API key not configured")
        print(f"   - Sender email not verified")
        print(f"   - Daily email limit reached")
    
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_otp_email()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()

