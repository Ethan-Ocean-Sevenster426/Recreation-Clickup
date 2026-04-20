#!/usr/bin/env python
"""
Script to create/update admin user profile with full admin permissions
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from main.models import User
from home.models import UserProfile

def fix_admin_profile():
    """Create or update admin user profile with full permissions"""
    try:
        admin = User.objects.get(username='admin')
        print(f"Found admin user: {admin.username}")
        print(f"  Role: {admin.role}")
        print(f"  Is Staff: {admin.is_staff}")
        print(f"  Is Superuser: {admin.is_superuser}")

        # Check if profile exists
        try:
            profile = UserProfile.objects.get(user=admin)
            print("\nUserProfile exists - updating permissions...")
            created = False
        except UserProfile.DoesNotExist:
            print("\nUserProfile does NOT exist - creating new profile...")
            profile = UserProfile(user=admin)
            created = True

        # Set all admin permissions to True
        profile.can_access_dashboard = True
        profile.can_access_projects = True
        profile.can_access_reports = True
        profile.can_access_analytics = True
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
        profile.can_access_system_logs = True

        profile.save()

        if created:
            print("[SUCCESS] UserProfile created with full admin permissions!")
        else:
            print("[SUCCESS] UserProfile updated with full admin permissions!")

        print("\nProfile permissions:")
        print(f"  can_access_admin: {profile.can_access_admin}")
        print(f"  can_manage_users: {profile.can_manage_users}")
        print(f"  can_manage_clients: {profile.can_manage_clients}")
        print(f"  can_create_projects: {profile.can_create_projects}")
        print(f"  can_edit_projects: {profile.can_edit_projects}")
        print(f"  can_delete_projects: {profile.can_delete_projects}")
        print(f"  can_view_system_logs: {profile.can_view_system_logs}")

        print("\n[SUCCESS] Admin profile is now fully configured!")
        print("Please refresh the admin panel page to see full access.")

    except User.DoesNotExist:
        print("[ERROR] Admin user does not exist!")
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_admin_profile()
