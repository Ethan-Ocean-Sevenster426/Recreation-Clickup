"""
Update credentials for CBH-Tigane client
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from home.models import Client

print("=" * 70)
print("  UPDATE CBH-TIGANE CREDENTIALS")
print("=" * 70)

try:
    # Get the client
    client = Client.objects.get(username="CBH-Tigane")

    print(f"\nFound client: {client.username}")
    print(f"Email: {client.email}")
    print(f"Client ID: {client.id}")

    # New credentials
    new_username = "CBH-Tigane"  # Keeping same username
    new_password = "CBH@Tigane2025!"  # New secure password

    # Update credentials
    client.username = new_username
    client.password = make_password(new_password)
    client.has_changed_password = True
    client.save()

    print("\n" + "=" * 70)
    print("  NEW CREDENTIALS")
    print("=" * 70)
    print(f"\nUsername: {new_username}")
    print(f"Password: {new_password}")
    print(f"Email: {client.email}")
    print("\n✓ Credentials updated successfully!")
    print("=" * 70)

except Client.DoesNotExist:
    print("\nERROR: Client 'CBH-Tigane' not found in database")
    sys.exit(1)
except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
