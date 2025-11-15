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
                "email": email
            }
        ],
        "subject": "Your OTP Code for Retail CRM",
        "htmlContent": f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .otp-box {{ background: linear-gradient(135deg, #5a1a8b 0%, #47136d 100%); 
                           color: white; padding: 30px; text-align: center; border-radius: 10px; 
                           margin: 20px 0; }}
                .otp-code {{ font-size: 32px; font-weight: bold; letter-spacing: 5px; 
                           margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Your OTP Code</h2>
                <p>Use the following code to complete your login:</p>
                <div class="otp-box">
                    <div class="otp-code">{otp_code}</div>
                </div>
                <p>This code will expire in 10 minutes.</p>
                <p>If you didn't request this code, please ignore this email.</p>
            </div>
        </body>
        </html>
        """,
        "textContent": f"Your OTP code is: {otp_code}\n\nThis code will expire in 10 minutes.\n\nIf you didn't request this code, please ignore this email."
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending OTP via Brevo: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return False


def create_and_send_otp(email, user=None):
    """
    Create an OTP code and send it via Brevo
    Returns the OTP code object if successful, None otherwise
    """
    # Delete any existing OTP codes for this email
    OTPCode.objects.filter(email=email, is_used=False).delete()
    
    # Generate new OTP
    otp_code = generate_otp()
    
    # Create OTP record
    otp = OTPCode.objects.create(
        email=email,
        code=otp_code,
        user=user,
        expires_at=datetime.now() + timedelta(minutes=10)
    )
    
    # Send OTP via Brevo
    if send_otp_via_brevo(email, otp_code):
        return otp
    else:
        # If sending fails, delete the OTP record
        otp.delete()
        return None


def verify_otp(email, code):
    """
    Verify an OTP code
    Returns the user if valid, None otherwise
    """
    try:
        otp = OTPCode.objects.get(
            email=email,
            code=code,
            is_used=False,
            expires_at__gt=datetime.now()
        )
        
        # Mark OTP as used
        otp.is_used = True
        otp.save()
        
        return otp.user
    except OTPCode.DoesNotExist:
        return None

