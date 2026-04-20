import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import DevMessage, User

print("=" * 80)
print("CLEANING MESSAGES AND CREATING TEST MESSAGE")
print("=" * 80)

# Delete all existing messages
message_count = DevMessage.objects.all().count()
print(f"\nFound {message_count} existing messages")

DevMessage.objects.all().delete()
print(f"[SUCCESS] Deleted all {message_count} messages")

# Create one test message
try:
    # Get admin user (or create if doesn't exist)
    admin_user = User.objects.filter(is_superuser=True).first()

    if not admin_user:
        print("\n[WARNING] No admin user found. Using first available user.")
        admin_user = User.objects.first()

    if admin_user:
        # Create test message
        test_message = DevMessage.objects.create(
            user=admin_user,
            message_type='feedback',
            subject='Test Message - System Check',
            message='This is a test message to verify the messaging system is working correctly. All filters, search, and mark-as-read features should work with this message.',
            priority='medium',
            status='new'
        )

        print(f"\n[SUCCESS] Created test message!")
        print(f"  ID: {test_message.id}")
        print(f"  From: {admin_user.username}")
        print(f"  Subject: {test_message.subject}")
        print(f"  Status: {test_message.status}")
        print(f"  Type: {test_message.message_type}")
    else:
        print("\n[ERROR] No users found in database. Cannot create test message.")

except Exception as e:
    print(f"\n[ERROR] Failed to create test message: {e}")

print("\n" + "=" * 80)
print("SCRIPT COMPLETED")
print("=" * 80)
print("\nEmail notifications will now be sent to: ethan.sevenster@moc-pty.com")
print("Refresh the page at http://127.0.0.1:8000/eclick-chats/ to see the test message")
print("=" * 80)
