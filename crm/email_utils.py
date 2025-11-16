import logging
import requests
import os
import json
from django.conf import settings
from threading import Thread

logger = logging.getLogger(__name__)

def check_sender_status(sender_email=None):
    """
    Check if sender email is verified in Brevo
    Returns: (is_verified, status_message)
    """
    try:
        api_key = os.environ.get('BREVO_API_KEY') or getattr(settings, 'BREVO_API_KEY', None)
        if not api_key:
            return False, "API key not configured"
        
        if not sender_email:
            sender_email = getattr(settings, 'BREVO_SENDER_EMAIL', 'ggvpby6996@gmail.com')
        
        url = "https://api.brevo.com/v3/senders"
        headers = {
            'accept': 'application/json',
            'api-key': api_key
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            senders = response.json().get('senders', [])
            for sender in senders:
                if sender.get('email', '').lower() == sender_email.lower():
                    verified = sender.get('verified', False)
                    status = sender.get('status', 'unknown')
                    if verified and status == 'valid':
                        return True, "Sender email is verified"
                    else:
                        return False, f"Sender email not verified. Status: {status}"
            return False, f"Sender email '{sender_email}' not found in Brevo account"
        else:
            return None, f"Could not check sender status (API returned {response.status_code})"
    except Exception as e:
        return None, f"Error checking sender status: {str(e)}"


def send_email_via_brevo(subject, html_content, text_content, recipients):
    """
    Send email via Brevo API with improved error handling and verification checks
    """
    try:
        # Get API key from env or settings fallback
        api_key = os.environ.get('BREVO_API_KEY') or getattr(settings, 'BREVO_API_KEY', None)
        if not api_key:
            logger.error("❌ Brevo API key not configured")
            print("❌ Brevo API key not found - check Render environment variables")
            return False
        
        # Dev mode bypass
        if os.getenv("DJANGO_DEVELOPMENT", "0") == "1":
            print(f"📧 DEVELOPMENT MODE - Email would be sent to: {recipients}")
            print(f"📧 SUBJECT: {subject}")
            print(f"📧 CONTENT: {text_content}")
            return True
        
        sender_email = getattr(settings, 'BREVO_SENDER_EMAIL', 'ggvpby6996@gmail.com')
        sender_name = getattr(settings, 'BREVO_SENDER_NAME', 'Retail CRM')
        
        # Check sender verification status (only log, don't block)
        is_verified, status_msg = check_sender_status(sender_email)
        if is_verified is False:
            print(f"⚠️  WARNING: {status_msg}")
            print(f"💡 Verify sender at: https://app.brevo.com/settings/senders")
        elif is_verified:
            print(f"✅ Sender email verified")
        
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            'accept': 'application/json',
            'api-key': api_key,
            'content-type': 'application/json'
        }
        
        payload = {
            "sender": {
                "name": sender_name,
                "email": sender_email
            },
            "to": [{"email": email} for email in recipients],
            "subject": subject,
            "htmlContent": html_content,
            "textContent": text_content
        }
        
        print(f"📧 Sending email to: {recipients}")
        print(f"📧 From: {sender_name} <{sender_email}>")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"📧 Brevo API response: {response.status_code}")
        
        if response.status_code in [200, 201]:
            logger.info(f"✅ Email sent successfully to {recipients}")
            print(f"✅ Email queued for delivery. Check inbox (and spam folder) for: {recipients}")
            
            # Get message ID if available
            try:
                response_data = response.json()
                if 'messageId' in response_data:
                    print(f"📬 Message ID: {response_data['messageId']}")
                    print(f"🔍 Track at: https://app.brevo.com/statistics/email")
            except:
                pass
            
            if not is_verified:
                print(f"⚠️  IMPORTANT: If email doesn't arrive, verify sender email in Brevo dashboard")
            
            return True
        else:
            error_msg = response.text
            logger.error(f"❌ Brevo API error: {response.status_code} - {error_msg}")
            print(f"❌ Brevo API error: {response.status_code}")
            
            # Parse and show helpful error messages
            try:
                error_data = json.loads(error_msg)
                if 'message' in error_data:
                    print(f"❌ Error: {error_data['message']}")
                if 'code' in error_data:
                    print(f"❌ Error code: {error_data['code']}")
            except:
                print(f"❌ Error details: {error_msg}")
            
            if response.status_code == 400:
                print("💡 Tip: Make sure sender email is verified in Brevo dashboard (Settings → Senders)")
            elif response.status_code == 401:
                print("💡 Tip: Check that BREVO_API_KEY is correct in environment variables")
            elif response.status_code == 402:
                print("💡 Tip: You've reached your daily email limit (free tier: 300/day)")
                print("💡 Check usage at: https://app.brevo.com/statistics/email")
            
            return False
    except requests.exceptions.Timeout:
        logger.error("❌ Request timeout - Brevo API took too long to respond")
        print("❌ Request timeout - please try again")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Network error: {str(e)}")
        print(f"❌ Network error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Error sending email: {str(e)}")
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def send_email_async(subject, html, text, recipients):
    """Send email asynchronously using Brevo API"""
    def send():
        result = send_email_via_brevo(subject, html, text, recipients)
        if not result:
            # Fallback to console
            print(f"📧 [FALLBACK] To: {recipients}")
            print(f"📧 [SUBJECT]: {subject}")
            print(f"📧 [CONTENT]: {text}")
    thread = Thread(target=send)
    thread.daemon = True
    thread.start()

def send_simple_email_async(subject, message, recipient_email):
    """
    Simple email wrapper for OTP and notifications
    """
    # Create clean text version
    text_message = message.replace('<div class=\'otp\'>', '').replace('</div>', '')
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #5a1a8b; color: white; padding: 20px; text-align: center; }}
            .content {{ background: #f9f9f9; padding: 20px; }}
            .otp {{ font-size: 24px; font-weight: bold; color: #5a1a8b; text-align: center; margin: 20px 0; padding: 10px; border: 2px dashed #5a1a8b; background: #f0f8ff; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
            .notification-message {{ background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #5a1a8b; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Retail CRM</h1>
            </div>
            <div class="content">
                <div class="notification-message">
                    {message}
                </div>
            </div>
            <div class="footer">
                <p>This is an automated message from Retail CRM</p>
            </div>
        </div>
    </body>
    </html>
    """
    send_email_async(
        subject=subject,
        html=html_content,
        text=text_message,
        recipients=[recipient_email]
    )
