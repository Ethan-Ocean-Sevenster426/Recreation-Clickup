import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = 'Chris'
email = 'chris@example.com'
password = 'Chris 2025!'

if User.objects.filter(username=username).exists():
    print(f'User "{username}" already exists')
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser "{username}" created successfully!')
