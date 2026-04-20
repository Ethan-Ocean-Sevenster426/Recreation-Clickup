#!/usr/bin/env python
"""
Script to set admin user password to 'admin123'
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from main.models import User
from django.contrib.auth import authenticate

def set_admin_password():
    """Set admin user password to 'admin123'"""
    try:
        # Get the admin user
        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            print("[ERROR] User 'admin' does not exist!")
            return

        print(f"Found user: {user.username}")
        print(f"Current details:")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role}")
        print(f"  Is Staff: {user.is_staff}")
        print(f"  Is Superuser: {user.is_superuser}")

        # Set password to 'admin123'
        print("\n[ACTION] Setting password to 'admin123'...")
        user.set_password('admin123')

        # Ensure admin role and permissions
        print("[ACTION] Ensuring admin role and permissions...")
        user.role = 'admin'
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.can_login = True

        # Save changes
        user.save()

        print("\n[SUCCESS] User 'admin' has been updated!")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Password: admin123")
        print(f"  Role: {user.role}")
        print(f"  Is Staff: {user.is_staff}")
        print(f"  Is Superuser: {user.is_superuser}")
        print(f"  Is Active: {user.is_active}")

        # Test authentication
        print("\n[TEST] Testing authentication...")
        test_user = authenticate(username='admin', password='admin123')
        if test_user:
            print("[SUCCESS] Authentication test PASSED!")
            print("\n" + "="*60)
            print("You can now login with:")
            print("  Username: admin")
            print("  Password: admin123")
            print("="*60)
        else:
            print("[ERROR] Authentication test FAILED!")

    except Exception as e:
        print(f"[ERROR] Error updating admin user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    set_admin_password()
