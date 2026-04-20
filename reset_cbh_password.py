"""
Reset password for CBH-Tigane client and send OTP email
"""

import os
import sys
import django
from datetime import timedelta
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.hashers import make_password
from home.models import Client, ClientOTP
from home.email_service import SimpleEmailService

print("=" * 70)
print("  RESET PASSWORD FOR CBH-TIGANE CLIENT")
print("=" * 70)

# Get the client
try:
    client = Client.objects.get(username="CBH-Tigane")
    print(f"\nFound client: {client.username}")
    print(f"Email: {client.email}")
    print(f"Client ID: {client.id}")
except Client.DoesNotExist:
    print("\nERROR: Client 'CBH-Tigane' not found")
    sys.exit(1)

# Set password to "123" temporarily for testing
print("\n[STEP 1] Setting current password to '123' for testing...")
client.password = make_password("123")
client.save()
print("Password set to: 123")

# Generate OTP
print("\n[STEP 2] Generating OTP for password reset...")
otp = ''.join(random.choices('0123456789', k=6))
print(f"Generated OTP: {otp}")

# Mark all existing OTPs as used
existing_otps = ClientOTP.objects.filter(client=client, is_used=False).count()
if existing_otps > 0:
    ClientOTP.objects.filter(client=client).update(is_used=True)
    print(f"Marked {existing_otps} existing OTP(s) as used")

# Create new OTP record
otp_obj = ClientOTP.objects.create(
    client=client,
    otp=otp,
    is_used=False,
    expires_at=timezone.now() + timedelta(minutes=10)
)
print(f"OTP record created (expires in 10 minutes)")
print(f"Expires at: {otp_obj.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")

# Send OTP email
print("\n[STEP 3] Sending OTP email...")
email_service = SimpleEmailService()

email_body = f"""
Dear {client.username},

You have requested a password reset for your E-Click client account.

Your OTP Code: {otp}

This OTP will expire in 10 minutes.

To reset your password, please visit:
http://127.0.0.1:8000/client/reset-password/?username={client.username}

Enter the OTP code above and your new password.

If you did not request this password reset, please ignore this email.

Best regards,
E-Click Team
"""

try:
    email_result = email_service.send_email(
        to_email=client.email,
        subject="Password Reset OTP - E-Click",
        body=email_body,
        from_email=None
    )

    if email_result['success']:
        print(f"SUCCESS! Email sent to: {client.email}")
        print(f"Message: {email_result.get('message', 'Email sent')}")
    else:
        print(f"ERROR! Email failed to send")
        print(f"Error: {email_result.get('error', 'Unknown error')}")

except Exception as e:
    print(f"ERROR! Exception sending email: {str(e)}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 70)
print("  SUMMARY")
print("=" * 70)
print(f"\nClient: {client.username}")
print(f"Email: {client.email}")
print(f"Current Password: 123")
print(f"\nOTP Code: {otp}")
print(f"OTP Valid Until: {otp_obj.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\nReset URL: http://127.0.0.1:8000/client/reset-password/?username={client.username}")
print("\nNext Steps:")
print("1. Check your email at: ethansevenster621@gmail.com")
print("2. Open the reset password URL above")
print(f"3. Enter OTP: {otp}")
print("4. Enter new password (minimum 8 characters)")
print("5. Confirm password")
print("6. Submit to reset password")
print("\nCurrent Login Credentials:")
print(f"  Username: {client.username}")
print("  Password: 123")
print("\n" + "=" * 70)
