"""
Check what clients exist in the E-Click database
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import Client

print("=" * 70)
print("  E-CLICK CLIENTS IN DATABASE")
print("=" * 70)

clients = Client.objects.all()

if clients.count() == 0:
    print("\nNo clients found in database.")
else:
    print(f"\nFound {clients.count()} client(s):\n")
    for i, client in enumerate(clients, 1):
        print(f"{i}. Username: {client.username}")
        print(f"   Email: {client.email}")
        print(f"   ID: {client.id}")
        print(f"   Is Active: {client.is_active}")
        print()

print("=" * 70)
