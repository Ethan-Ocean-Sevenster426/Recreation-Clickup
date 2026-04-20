import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = 'Chris'
password = 'Chris2025!'

user = User.objects.get(username=username)
user.set_password(password)
user.save()
print(f'Password updated successfully for user "{username}"')
