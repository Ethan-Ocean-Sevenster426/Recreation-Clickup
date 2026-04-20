#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

try:
    # Get User 2
    user = User.objects.get(username='User 2')
    
    # Set a new password
    user.set_password('testpass123')
    user.save()
    
    print(f"Password set successfully for user: {user.username}")
    print(f"Email: {user.email}")
    print(f"Is active: {user.is_active}")
    print(f"Is staff: {user.is_staff}")
    print(f"Is superuser: {user.is_superuser}")
    
    # Check if user has projects assigned
    from home.models import Project
    assigned_projects = user.assigned_projects.all()
    print(f"\nAssigned projects: {[p.name for p in assigned_projects]}")
    
except User.DoesNotExist:
    print("User 'User 2' not found")
except Exception as e:
    print(f"Error: {e}")
