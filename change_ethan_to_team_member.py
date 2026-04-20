import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import User

print("=" * 80)
print("CHANGING ETHAN TO TEAM MEMBER")
print("=" * 80)

try:
    ethan = User.objects.get(username='ethan')

    print(f"\nCurrent status:")
    print(f"  Username: {ethan.username}")
    print(f"  Email: {ethan.email}")
    print(f"  Is Staff: {ethan.is_staff}")
    print(f"  Is Superuser: {ethan.is_superuser}")

    # Change to team member (staff but not superuser)
    ethan.is_staff = True
    ethan.is_superuser = False
    ethan.save()

    print(f"\n[SUCCESS] Updated Ethan to team member status!")
    print(f"\nNew status:")
    print(f"  Username: {ethan.username}")
    print(f"  Email: {ethan.email}")
    print(f"  Is Staff: {ethan.is_staff}")
    print(f"  Is Superuser: {ethan.is_superuser}")
    print(f"  Password: Ethan123!")

except User.DoesNotExist:
    print("[ERROR] User 'ethan' not found in database!")
except Exception as e:
    print(f"[ERROR] An error occurred: {e}")

print("\n" + "=" * 80)
print("SCRIPT COMPLETED")
print("=" * 80)
