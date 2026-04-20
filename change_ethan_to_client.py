import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import User

print("=" * 80)
print("CHANGING ETHAN FROM ADMIN TO CLIENT")
print("=" * 80)

# Find Ethan user
try:
    ethan = User.objects.get(username='ethan')

    print(f"\n[FOUND] User: {ethan.username}")
    print(f"Current status:")
    print(f"  - Email: {ethan.email}")
    print(f"  - Full Name: {ethan.get_full_name()}")
    print(f"  - Is Staff: {ethan.is_staff}")
    print(f"  - Is Superuser: {ethan.is_superuser}")
    print(f"  - Is Active: {ethan.is_active}")

    # Remove staff and superuser privileges
    ethan.is_staff = False
    ethan.is_superuser = False
    ethan.save()

    print(f"\n[SUCCESS] Ethan has been changed to a regular client!")
    print(f"\nNew status:")
    print(f"  - Is Staff: {ethan.is_staff}")
    print(f"  - Is Superuser: {ethan.is_superuser}")
    print(f"  - Is Active: {ethan.is_active}")

    print(f"\n[INFO] Ethan can now:")
    print(f"  - Login to the client dashboard")
    print(f"  - View assigned projects")
    print(f"  - Send messages to developers")
    print(f"  - Use the chatbot")

    print(f"\n[INFO] Ethan CANNOT:")
    print(f"  - Access admin features")
    print(f"  - View satisfaction reports")
    print(f"  - Manage users")
    print(f"  - Access system logs")

except User.DoesNotExist:
    print(f"\n[ERROR] User 'ethan' not found!")
except Exception as e:
    print(f"\n[ERROR] An error occurred: {e}")

print("\n" + "=" * 80)
print("SCRIPT COMPLETED")
print("=" * 80)
