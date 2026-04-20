#!/usr/bin/env python
"""Create test user for password reset testing"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Find existing user by email
email = 'ethansevenster5@gmail.com'

try:
    user = User.objects.get(email=email)
    print(f"Found existing user: {user.username}")
    print(f"User ID: {user.pk}")
except User.DoesNotExist:
    print(f"No user found with email: {email}")
    print("Creating new test user...")
    user = User.objects.create_user(
        username='test_reset_user',
        email=email,
        password='oldpassword123'
    )
    print(f"Created new user: {user.username}")

print(f"Email: {email}")
print(f"Password: oldpassword123")
print(f"\nYou can now test the password reset by:")
print(f"1. Go to http://127.0.0.1:8000/login/")
print(f"2. Click 'Forgot Password?'")
print(f"3. Enter email: {email}")
print(f"4. Check the console/email for the reset link")
