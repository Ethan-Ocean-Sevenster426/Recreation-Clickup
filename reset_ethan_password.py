"""
Reset Ethan client account password.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import Client
from django.contrib.auth.hashers import make_password

def reset_ethan_password():
    """Reset Ethan's password"""
    username = 'Ethan'
    new_password = 'Ethan2025!'

    try:
        client = Client.objects.get(username=username)
        print(f"[OK] Found client: {client.username} ({client.email})")

        # Set password using Django's password hasher
        client.password = make_password(new_password)
        client.has_changed_password = True
        client.is_active = True
        client.save()

        print(f"[OK] Password updated successfully")
        print(f"\n" + "=" * 60)
        print("CLIENT LOGIN CREDENTIALS")
        print("=" * 60)
        print(f"Username: {username}")
        print(f"Password: {new_password}")
        print(f"Email: {client.email}")
        print(f"Status: {'Active' if client.is_active else 'Inactive'}")
        print("=" * 60)
        print(f"\nThe client can now login at http://127.0.0.1:8000/login/")

    except Client.DoesNotExist:
        print(f"[FAIL] Client '{username}' not found")
        print("\nCreating new client account...")

        # Create new client
        client = Client.objects.create(
            username=username,
            email='ethan@example.com',
            password=make_password(new_password),
            has_changed_password=True,
            is_active=True
        )

        print(f"[OK] Created new client: {client.username}")
        print(f"\n" + "=" * 60)
        print("NEW CLIENT ACCOUNT CREATED")
        print("=" * 60)
        print(f"Username: {username}")
        print(f"Password: {new_password}")
        print(f"Email: {client.email}")
        print("=" * 60)
        print(f"\nThe client can now login at http://127.0.0.1:8000/login/")

if __name__ == "__main__":
    print("=" * 60)
    print("Resetting Ethan Client Password")
    print("=" * 60)
    print()

    reset_ethan_password()
