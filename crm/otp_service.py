"""
Brevo API integration for OTP (One-Time Password) service
"""
import random
import string
from datetime import timedelta

from django.utils import timezone

from .models import OTPCode
from .email_utils import send_simple_email_async


def _normalize_email(email: str) -> str:
    """Normalize email for consistent OTP lookups."""
    return (email or '').strip().lower()


def generate_otp(length=6):
    """Generate a random OTP code"""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_via_brevo(email, otp_code):
    """
    Send OTP code via Brevo (using async email utility)
    """
    subject = "Your OTP Code for Retail CRM"
    message = f"""
        <div>
            <p>Your One-Time Password (OTP) for Retail CRM is:</p>
            <div class='otp' style='font-size:2em;letter-spacing:5px;text-align:center;margin:20px 0;padding:15px;background:#f1e6ff;color:#5a1a8b;border-radius:10px;border:2px dashed #5a1a8b;display:inline-block;'>{otp_code}</div>
            <p>This code will expire in 10 minutes.</p>
            <p>If you did not request this code, please ignore this email or contact support.</p>
        </div>
    """
    print(f"📧 CRM OTP DEBUG: About to send OTP to {email}: {otp_code}")
    send_simple_email_async(subject, message, email)
    print(f"📧 CRM OTP DEBUG: send_simple_email_async call completed for {email}")
    return True


def create_and_send_otp(email, user=None):
    """
    Create an OTP code and send it via Brevo
    Returns the OTP code object if successful, None otherwise
    """
    try:
        normalized_email = _normalize_email(email)
        display_email = email.strip()

        # Delete any existing unused OTP codes for this email
        deleted_count = OTPCode.objects.filter(email=normalized_email, is_used=False).delete()[0]
        if deleted_count > 0:
            print(f"Deleted {deleted_count} old OTP(s) for {email}")
        
        # Generate new OTP
        otp_code = generate_otp()
        print(f"Generated OTP: {otp_code} for {email}")
        
        # Create OTP record
        otp = OTPCode.objects.create(
            email=normalized_email,
            code=otp_code,
            user=user,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        print(f"OTP record created in database. Expires at: {otp.expires_at}")
        
        # Send OTP via Brevo
        if send_otp_via_brevo(display_email or normalized_email, otp_code):
            print(f"✅ OTP process completed successfully for {email}")
            return otp
        else:
            # If sending fails, delete the OTP record
            print(f"❌ Failed to send OTP, deleting record for {email}")
            otp.delete()
            return None
    except Exception as e:
        print(f"❌ Error in create_and_send_otp: {e}")
        return None


def verify_otp(email, code):
    """
    Verify an OTP code
    Returns the user if valid, None otherwise
    """
    try:
        print(f"Attempting to verify OTP for {email} with code: {code}")
        
        normalized_email = _normalize_email(email)

        otp = OTPCode.objects.get(
            email=normalized_email,
            code=code,
            is_used=False,
            expires_at__gt=timezone.now()
        )
        
        print(f"✅ Valid OTP found for {email}")
        
        # Mark OTP as used
        otp.is_used = True
        otp.save()
        
        print(f"✅ OTP marked as used for {email}")
        
        return otp.user
    except OTPCode.DoesNotExist:
        print(f"❌ Invalid or expired OTP for {email}")
        
        # Debug: Check what OTPs exist for this email
        all_otps = OTPCode.objects.filter(email=normalized_email)
        print(f"Debug: Found {all_otps.count()} OTP(s) for {email}:")
        for otp in all_otps:
            print(f"  - Code: {otp.code}, Used: {otp.is_used}, Expires: {otp.expires_at}")
        
        return None
    except Exception as e:
        print(f"❌ Error verifying OTP: {e}")
        return None


def resend_otp(email, user=None):
    """
    Resend OTP code - same as create_and_send_otp but with logging
    """
    try:
        normalized_email = _normalize_email(email)
        display_email = email.strip()

        print(f"🔄 Resending OTP for {display_email or normalized_email}...")
        # Delete any existing unused OTP codes for this email
        deleted_count = OTPCode.objects.filter(email=normalized_email, is_used=False).delete()[0]
        if deleted_count > 0:
            print(f"Deleted {deleted_count} old OTP(s) for {email}")
        # Generate new OTP
        otp_code = generate_otp()
        print(f"Generated new OTP: {otp_code} for {email}")
        # Create OTP record
        otp = OTPCode.objects.create(
            email=normalized_email,
            code=otp_code,
            user=user,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        print(f"New OTP record created. Expires at: {otp.expires_at}")
        # Send OTP via Brevo
        if send_otp_via_brevo(display_email or normalized_email, otp_code):
            print(f"✅ OTP resent successfully to {display_email or normalized_email}")
            return otp
        else:
            print(f"❌ Failed to resend OTP, deleting record for {email}")
            otp.delete()
            return None
    except Exception as e:
        print(f"❌ Error in resend_otp: {e}")
        return None
        