"""
Check what users exist in the E-Click database
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import User

print("=" * 70)
print("  E-CLICK USERS IN DATABASE")
print("=" * 70)

users = User.objects.all()

if users.count() == 0:
    print("\nNo users found in database.")
else:
    print(f"\nFound {users.count()} user(s):\n")
    for i, user in enumerate(users, 1):
        print(f"{i}. Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   ID: {user.id}")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Is Active: {user.is_active}")
        print()

print("=" * 70)
