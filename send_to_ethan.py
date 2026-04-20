"""
Send test emails to Ethan's accounts only
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.core.mail import send_mail

print("="*70)
print("SENDING TEST EMAILS TO ETHAN")
print("="*70)

# Ethan's email addresses only
recipients = [
    'ethan.sevenster@moc-pty.com',
    'ethansevenster5@gmail.com'
]

for email in recipients:
    print(f"\nSending to: {email}")
    try:
        send_mail(
            subject='E-Click Test Email',
            message='Hi Ethan,\n\nThis is a test email from the E-Click system.\n\nIf you receive this, email delivery is working correctly!\n\nBest regards,\nE-Click System',
            from_email='info@eclick.co.za',
            recipient_list=[email],
            fail_silently=False,
        )
        print(f"  [OK] Sent to {email}")
    except Exception as e:
        print(f"  [FAIL] Error: {e}")

print("\n" + "="*70)
print("DONE - Check your inbox")
print("="*70)
