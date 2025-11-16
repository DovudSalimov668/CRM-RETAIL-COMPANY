"""
Check if sender email is verified in Brevo
Run: python check_sender_status.py
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

from crm.email_utils import check_sender_status
from django.conf import settings

def main():
    print("=" * 60)
    print("Checking Brevo Sender Email Status")
    print("=" * 60)
    
    sender_email = getattr(settings, 'BREVO_SENDER_EMAIL', 'ggvpby6996@gmail.com')
    print(f"\nSender Email: {sender_email}")
    print("-" * 60)
    
    is_verified, status_msg = check_sender_status(sender_email)
    
    if is_verified is True:
        print(f"\n✅ {status_msg}")
        print("\n✅ Your sender email is verified and ready to send emails!")
    elif is_verified is False:
        print(f"\n❌ {status_msg}")
        print("\n⚠️  ACTION REQUIRED:")
        print(f"   1. Go to: https://app.brevo.com/settings/senders")
        print(f"   2. Find or add: {sender_email}")
        print(f"   3. Click 'Verify' and check your email inbox")
        print(f"   4. Click the verification link in the email")
    else:
        print(f"\n⚠️  {status_msg}")
        print("\n💡 Could not check status. Make sure:")
        print("   - BREVO_API_KEY is set correctly")
        print("   - You have internet connection")
        print("   - Your Brevo account is active")
    
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()

