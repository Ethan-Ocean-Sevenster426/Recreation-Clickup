#!/usr/bin/env python
"""
Test script to create a user named Ethan with admin role
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick_project.settings')
django.setup()

from main.models import User
from home.models import UserProfile

def create_test_user():
    """Create a test user named Ethan with admin role"""
    try:
        # Check if user already exists
        if User.objects.filter(username='ethan').exists():
            print("User 'ethan' already exists!")
            user = User.objects.get(username='ethan')
            print(f"Existing user details:")
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Role: {getattr(user, 'role', 'No role field')}")
            print(f"  Is Staff: {user.is_staff}")
            print(f"  Is Superuser: {user.is_superuser}")
            return

        # Create new user
        print("Creating user 'ethan'...")
        user = User.objects.create_user(
            username='ethan',
            email='ethan@example.com',
            password='admin123',  # Change this to a secure password
            first_name='Ethan',
            last_name='Admin',
            role='admin'  # Set admin role
        )

        # Set admin permissions
        user.is_staff = True
        user.is_superuser = True
        user.save()

        print(f"[SUCCESS] User created successfully!")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role}")
        print(f"  Is Staff: {user.is_staff}")
        print(f"  Is Superuser: {user.is_superuser}")

        # Create user profile with admin permissions
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
            if created:
                print(f"[SUCCESS] User profile created with full admin permissions")
            else:
                print(f"[INFO] User profile already exists")
        except Exception as e:
            print(f"[WARNING] Could not create user profile: {e}")

        print("\nYou can now login with:")
        print(f"  Username: ethan")
        print(f"  Password: admin123")

    except Exception as e:
        print(f"[ERROR] Error creating user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_test_user()
