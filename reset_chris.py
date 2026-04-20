import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Find and update Chris
chris = User.objects.get(username='Chris')
chris.set_password('password123')
chris.save()

print(f"[OK] Password updated for {chris.username}")
print(f"     Email: {chris.email}")
print(f"     New password: password123")
