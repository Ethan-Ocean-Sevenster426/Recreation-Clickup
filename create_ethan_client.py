#!/usr/bin/env python
"""Create Ethan as a client user for password reset testing"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import Client

# Client details
username = 'Ethan'
email = 'ethansevenster5@gmail.com'
password = 'testpassword123'

# Check if client already exists
existing_client = None
try:
    existing_client = Client.objects.get(username=username)
    print(f"Client with username '{username}' already exists")
    print(f"Client ID: {existing_client.pk}")
    print(f"Email: {existing_client.email}")
except Client.DoesNotExist:
    pass

if not existing_client:
    try:
        existing_client = Client.objects.get(email=email)
        print(f"Client with email '{email}' already exists")
        print(f"Username: {existing_client.username}")
        print(f"Client ID: {existing_client.pk}")
    except Client.DoesNotExist:
        pass

if not existing_client:
    # Create new client
    client = Client(
        username=username,
        email=email,
        company_name='Test Company'
    )
    client.set_password(password)
    client.save()

    print(f"Successfully created client user!")
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Client ID: {client.pk}")
else:
    # Update existing client's password
    existing_client.set_password(password)
    existing_client.email = email
    existing_client.save()
    print(f"\nUpdated existing client's password and email")
    print(f"Username: {existing_client.username}")
    print(f"Email: {email}")
    print(f"Password: {password}")

print(f"\n=== Test Password Reset ===")
print(f"1. Go to http://127.0.0.1:8000/password-reset/")
print(f"2. Enter username: {username} OR email: {email}")
print(f"3. Check email/console for reset link")
