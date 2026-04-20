"""
Send a test email to verify the email system is working
"""

import os
import sys
import django
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.email_service import SimpleEmailService

print("=" * 70)
print("  SEND TEST EMAIL")
print("=" * 70)

# Initialize email service
email_service = SimpleEmailService()

# Email details
to_email = "ethan.sevenster@moc-pty.com"
subject = "Test Email - E-Click System"

# Create email body
body = f"""<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2 style="color: #2563eb;">E-Click Email System Test</h2>

    <p>Hello Ethan,</p>

    <p>This is a test email to verify that the E-Click email system is working correctly.</p>

    <p><strong>Test Details:</strong></p>
    <ul>
        <li>Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
        <li>Email Service: SimpleEmailService</li>
        <li>OTP Expiration: 24 hours (recently updated)</li>
    </ul>

    <p>If you receive this email, the email system is functioning properly!</p>

    <p>Best regards,<br>
    E-Click Project Management Team</p>
</body>
</html>"""

print(f"\nSending test email to: {to_email}")
print(f"Subject: {subject}")

# Send the email
try:
    result = email_service.send_email(
        to_email=to_email,
        subject=subject,
        body=body,
        from_email=None  # Will use default from settings
    )

    print("\n" + "=" * 70)
    if result['success']:
        print("  SUCCESS!")
        print("=" * 70)
        print(f"\nEmail sent successfully to: {to_email}")
        print(f"Message: {result.get('message', 'Email sent')}")
    else:
        print("  FAILED!")
        print("=" * 70)
        print(f"\nError sending email to: {to_email}")
        print(f"Error: {result.get('error', 'Unknown error')}")

    print("\n" + "=" * 70)

except Exception as e:
    print("\n" + "=" * 70)
    print("  ERROR!")
    print("=" * 70)
    print(f"\nException occurred: {str(e)}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 70)
