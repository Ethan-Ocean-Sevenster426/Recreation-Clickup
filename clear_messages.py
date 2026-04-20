import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.contrib.sessions.models import Session
from django.contrib.messages.storage.session import SessionStorage
from django.contrib.messages import constants as message_constants

print("=" * 80)
print("CLEARING DJANGO MESSAGES")
print("=" * 80)

# Clear all sessions to remove accumulated messages
sessions = Session.objects.all()
print(f"\nFound {sessions.count()} sessions")

for session in sessions:
    session.delete()
    print(f"Cleared session: {session.session_key}")

print("\n[SUCCESS] All messages have been cleared!")
print("\nPlease log in again to create a fresh session.")
print("=" * 80)
