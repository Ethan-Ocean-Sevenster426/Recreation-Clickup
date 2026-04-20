import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import Client
from django.contrib.auth.hashers import make_password

def update_client_password():
    """Update client password for CBH-Tigane"""
    try:
        client = Client.objects.get(username='CBH-Tigane')

        print(f"Found client: {client.username} ({client.email})")

        # Update password
        new_password = "password123"
        client.password = make_password(new_password)
        client.has_changed_password = True
        client.save()

        print(f"[OK] Password updated successfully to: {new_password}")
        print(f"[OK] has_changed_password flag set to True")

    except Client.DoesNotExist:
        print(f"[FAIL] Client 'CBH-Tigane' not found in database")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

if __name__ == "__main__":
    update_client_password()
