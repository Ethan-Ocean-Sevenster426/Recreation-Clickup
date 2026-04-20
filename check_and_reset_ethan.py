import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import User
from django.contrib.auth.hashers import make_password

print("=" * 80)
print("CHECKING ALL USERS IN DATABASE")
print("=" * 80)

# Get all users
all_users = User.objects.all()
print(f"\nTotal users in database: {all_users.count()}\n")

# Display all users with their details
print("ALL USERS:")
print("-" * 80)
for user in all_users:
    print(f"Username: {user.username}")
    print(f"  - Email: {user.email}")
    print(f"  - Full Name: {user.get_full_name() or 'Not set'}")
    print(f"  - Is Staff: {user.is_staff}")
    print(f"  - Is Superuser: {user.is_superuser}")
    print(f"  - Is Active: {user.is_active}")
    print(f"  - Last Login: {user.last_login}")
    print("-" * 80)

# Check for Ethan user
print("\n" + "=" * 80)
print("SEARCHING FOR ETHAN USER")
print("=" * 80)

ethan_users = User.objects.filter(username__icontains='ethan')
if not ethan_users.exists():
    # Try searching by first name or email
    ethan_users = User.objects.filter(first_name__icontains='ethan') | User.objects.filter(email__icontains='ethan')

if ethan_users.exists():
    print(f"\n[FOUND] Found {ethan_users.count()} user(s) matching 'Ethan':\n")

    for user in ethan_users:
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Full Name: {user.get_full_name() or 'Not set'}")
        print(f"Is Staff: {user.is_staff}")
        print(f"Is Superuser: {user.is_superuser}")
        print("-" * 80)

        # Reset password for this user
        new_password = "Ethan123!"
        user.set_password(new_password)
        user.save()

        print(f"\n[SUCCESS] Password reset for user: {user.username}")
        print(f"\nCREDENTIALS:")
        print(f"  Username: {user.username}")
        print(f"  Password: {new_password}")
        print(f"  Email: {user.email}")
        print("=" * 80)
else:
    print("\n[NOT FOUND] No user matching 'Ethan' found in database.")
    print("\nWould you like to create a new user? (This script will create one now)")

    # Create new Ethan user
    new_username = "ethan"
    new_email = "ethan@eclick.com"
    new_password = "Ethan123!"

    # Check if username already exists
    if not User.objects.filter(username=new_username).exists():
        new_user = User.objects.create(
            username=new_username,
            email=new_email,
            first_name="Ethan",
            last_name="User",
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        new_user.set_password(new_password)
        new_user.save()

        print(f"\n[CREATED] New user created successfully!")
        print(f"\nCREDENTIALS:")
        print(f"  Username: {new_username}")
        print(f"  Password: {new_password}")
        print(f"  Email: {new_email}")
        print(f"  Is Staff: Yes")
        print(f"  Is Superuser: Yes")
        print("=" * 80)
    else:
        print(f"\n[ERROR] Username '{new_username}' already exists!")

print("\n" + "=" * 80)
print("SCRIPT COMPLETED")
print("=" * 80)
