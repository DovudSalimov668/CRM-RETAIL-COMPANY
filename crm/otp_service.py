"""
Brevo API integration for OTP (One-Time Password) service
"""
import os
import random
import string
from datetime import datetime, timedelta
from django.conf import settings
import requests
from .models import OTPCode
from django.utils import timezone


def generate_otp(length=6):
    """Generate a random OTP code"""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_via_brevo(email, otp_code):
    """
    Send OTP code via Brevo (formerly Sendinblue) API
    """
    brevo_api_key = os.getenv('BREVO_API_KEY')
    brevo_sender_email = os.getenv('BREVO_SENDER_EMAIL', 'noreply@retailcrm.com')
    brevo_sender_name = os.getenv('BREVO_SENDER_NAME', 'Retail CRM')
    
    if not brevo_api_key:
        print("ERROR: BREVO_API_KEY is not set in environment variables")
        raise ValueError("BREVO_API_KEY is not set in environment variables")
    
    url = "https://api.brevo.com/v3/smtp/email"
    
    headers = {
        "accept": "application/json",
        "api-key": brevo_api_key,
        "content-type": "application/json"
    }
    
    payload = {
        "sender": {
            "name": brevo_sender_name,
            "email": brevo_sender_email
        },
        "to": [
            {
                "email": email,
                "name": email.split('@')[0]  # Add recipient name
            }
        ],
        "subject": "Your OTP Code for Retail CRM",
        "htmlContent": f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 30px auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .otp-box {{ background: linear-gradient(135deg, #5a1a8b 0%, #47136d 100%); 
                           color: white; padding: 30px; text-align: center; border-radius: 10px; 
                           margin: 20px 0; }}
                .otp-code {{ font-size: 36px; font-weight: bold; letter-spacing: 8px; 
                           margin: 20px 0; font-family: 'Courier New', monospace; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Retail CRM Login</h1>
                </div>
                <h2 style="color: #333;">Your One-Time Password</h2>
                <p style="color: #666;">Use the following code to complete your login:</p>
                <div class="otp-box">
                    <div class="otp-code">{otp_code}</div>
                </div>
                <p style="color: #e74c3c; font-weight: bold;">⏰ This code will expire in 10 minutes.</p>
                <p style="color: #666;">If you didn't request this code, please ignore this email or contact support.</p>
                <div class="footer">
                    <p>© 2024 Retail CRM System. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """,
        "textContent": f"""Your OTP code is: {otp_code}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

- Retail CRM Team"""
    }
    
    try:
        print(f"Attempting to send OTP to {email}...")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✅ OTP sent successfully to {email}. Message ID: {response.json().get('messageId', 'N/A')}")
        return True
    except requests.exceptions.Timeout:
        print(f"❌ Timeout error sending OTP to {email}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending OTP via Brevo: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response Status: {e.response.status_code}")
            print(f"Response Body: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def create_and_send_otp(email, user=None):
    """
    Create an OTP code and send it via Brevo
    Returns the OTP code object if successful, None otherwise
    """
    try:
        # Delete any existing unused OTP codes for this email
        deleted_count = OTPCode.objects.filter(email=email, is_used=False).delete()[0]
        if deleted_count > 0:
            print(f"Deleted {deleted_count} old OTP(s) for {email}")
        
        # Generate new OTP
        otp_code = generate_otp()
        print(f"Generated OTP: {otp_code} for {email}")
        
        # Create OTP record
        otp = OTPCode.objects.create(
            email=email,
            code=otp_code,
            user=user,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        print(f"OTP record created in database. Expires at: {otp.expires_at}")
        
        # Send OTP via Brevo
        if send_otp_via_brevo(email, otp_code):
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
        
        otp = OTPCode.objects.get(
            email=email,
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
        all_otps = OTPCode.objects.filter(email=email)
        print(f"Debug: Found {all_otps.count()} OTP(s) for {email}:")
        for otp in all_otps:
            print(f"  - Code: {otp.code}, Used: {otp.is_used}, Expires: {otp.expires_at}")
        
        return None
    except Exception as e:
        print(f"❌ Error verifying OTP: {e}")
        return None
        