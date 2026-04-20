import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

result = send_mail(
    'E-Click Test Email',
    'This is a test email from E-Click Project Management System.\n\nIf you receive this, email delivery is working correctly.\n\nBest regards,\nE-Click Team',
    settings.DEFAULT_FROM_EMAIL,
    ['ethan.sevenster@moc-pty.com'],
    fail_silently=False,
)

print(f"Email sent to ethan.sevenster@moc-pty.com: {result}")
