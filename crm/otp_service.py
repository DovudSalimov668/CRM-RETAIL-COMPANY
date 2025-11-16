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
    Send OTP code via Brevo with improved email template
    """
    from .email_utils import send_email_via_brevo
    
    subject = "Your OTP Code for Retail CRM"
    
    # Improved HTML email template with better structure
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333333;
                background-color: #f5f5f5;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #5a1a8b, #47136d);
                color: #ffffff;
                padding: 30px 20px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                font-weight: 600;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .otp-box {{
                background: #f1e6ff;
                border: 2px dashed #5a1a8b;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                margin: 30px 0;
            }}
            .otp-code {{
                font-size: 32px;
                font-weight: bold;
                letter-spacing: 8px;
                color: #5a1a8b;
                font-family: 'Courier New', monospace;
                margin: 10px 0;
            }}
            .footer {{
                background: #f9f9f9;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #666666;
                border-top: 1px solid #eeeeee;
            }}
            .warning {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 12px;
                margin: 20px 0;
                border-radius: 4px;
                font-size: 13px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Retail CRM</h1>
            </div>
            <div class="content">
                <h2 style="color: #5a1a8b; margin-top: 0;">Your One-Time Password</h2>
                <p>Use this code to complete your login:</p>
                
                <div class="otp-box">
                    <div class="otp-code">{otp_code}</div>
                </div>
                
                <p style="margin-bottom: 0;"><strong>This code will expire in 10 minutes.</strong></p>
                
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong> If you did not request this code, please ignore this email or contact support immediately.
                </div>
            </div>
            <div class="footer">
                <p>This is an automated message from Retail CRM System</p>
                <p style="margin: 5px 0 0 0;">Please do not reply to this email</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_message = f"""
Retail CRM - Your One-Time Password

Your OTP code is: {otp_code}

This code will expire in 10 minutes.

If you did not request this code, please ignore this email or contact support immediately.

---
This is an automated message from Retail CRM System
    """
    
    print(f"📧 CRM OTP DEBUG: About to send OTP to {email}: {otp_code}")
    
    # Use synchronous sending for OTP so we can verify it worked
    result = send_email_via_brevo(subject, html_message, text_message, [email])
    
    if result:
        print(f"✅ CRM OTP DEBUG: OTP email sent successfully to {email}")
    else:
        print(f"❌ CRM OTP DEBUG: Failed to send OTP email to {email}")
    
    return result


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
        