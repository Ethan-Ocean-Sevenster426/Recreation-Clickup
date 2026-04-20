#!/usr/bin/env python
"""Verify and update Ethan client for password reset testing"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import Client
from django.contrib.auth.hashers import make_password

# Client details
username = 'Ethan'
email = 'ethansevenster5@gmail.com'
password = 'testpassword123'

try:
    client = Client.objects.get(username=username)
    print(f"Found client: {client.username}")
    print(f"Client ID: {client.pk}")
    print(f"Email: {client.email}")
    print(f"Is Active: {client.is_active}")
    print(f"Has Changed Password: {client.has_changed_password}")

    # Update password with Django hashing
    client.password = make_password(password)
    client.save()

    print(f"\n✓ Updated password for client '{username}'")
    print(f"\n=== Test Password Reset ===")
    print(f"1. Go to http://127.0.0.1:8000/password-reset/")
    print(f"2. Enter username: {username} OR email: {email}")
    print(f"3. Check your email inbox for the reset link")
    print(f"\nCurrent password: {password}")

except Client.DoesNotExist:
    print(f"Client '{username}' does not exist. Creating new client...")

    client = Client(
        username=username,
        email=email,
        company_name='Test Company'
    )
    client.password = make_password(password)
    client.save()

    print(f"Successfully created client user!")
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Client ID: {client.pk}")
