#!/usr/bin/env python
"""
Script to fix the admin user - set password to '123' and update role to 'admin'
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick_project.settings')
django.setup()

from main.models import User
from home.models import UserProfile

def fix_admin_user():
    """Fix admin user password and role"""
    try:
        # Get the admin user
        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            print("[ERROR] User 'admin' does not exist!")
            print("Available users:")
            for u in User.objects.all():
                print(f"  - {u.username} ({u.email})")
            return

        print(f"Found user: {user.username}")
        print(f"Current details:")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role}")
        print(f"  Is Staff: {user.is_staff}")
        print(f"  Is Superuser: {user.is_superuser}")
        print(f"  Is Active: {user.is_active}")

        # Set password to '123'
        print("\n[ACTION] Setting password to '123'...")
        user.set_password('123')

        # Update role to admin
        print("[ACTION] Updating role to 'admin'...")
        user.role = 'admin'

        # Ensure admin permissions
        print("[ACTION] Setting admin permissions...")
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True

        # Save changes
        user.save()

        print("\n[SUCCESS] User 'admin' has been updated!")
        print(f"New details:")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role}")
        print(f"  Password: 123")
        print(f"  Is Staff: {user.is_staff}")
        print(f"  Is Superuser: {user.is_superuser}")
        print(f"  Is Active: {user.is_active}")

        # Check/create user profile
        try:
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'can_access_dashboard': True,
                    'can_access_projects': True,
                    'can_access_reports': True,
                    'can_access_analytics': True,
                    'can_access_admin': True,
                    'can_manage_users': True,
                    'can_manage_clients': True,
                    'can_create_projects': True,
                    'can_edit_projects': True,
                    'can_delete_projects': True,
                    'can_create_tasks': True,
                    'can_edit_tasks': True,
                    'can_delete_tasks': True,
                    'can_view_system_logs': True,
                    'can_access_backup_management': True,
                    'can_access_system_monitoring': True,
                }
            )

            if not created:
                # Update existing profile with admin permissions
                profile.can_access_admin = True
                profile.can_manage_users = True
                profile.can_manage_clients = True
                profile.can_create_projects = True
                profile.can_edit_projects = True
                profile.can_delete_projects = True
                profile.can_create_tasks = True
                profile.can_edit_tasks = True
                profile.can_delete_tasks = True
                profile.can_view_system_logs = True
                profile.can_access_backup_management = True
                profile.can_access_system_monitoring = True
                profile.save()
                print("[SUCCESS] User profile updated with admin permissions")
            else:
                print("[SUCCESS] User profile created with admin permissions")

        except Exception as e:
            print(f"[WARNING] Could not update user profile: {e}")

        # Test authentication
        print("\n[TEST] Testing authentication...")
        from django.contrib.auth import authenticate
        test_user = authenticate(username='admin', password='123')
        if test_user:
            print("[SUCCESS] Authentication test PASSED!")
            print("\nYou can now login with:")
            print("  Username: admin")
            print("  Password: 123")
        else:
            print("[ERROR] Authentication test FAILED!")

    except Exception as e:
        print(f"[ERROR] Error fixing admin user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_admin_user()
