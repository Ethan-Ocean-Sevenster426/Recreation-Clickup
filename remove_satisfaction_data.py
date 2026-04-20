import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import ChatbotFeedback

print("=" * 80)
print("REMOVING SATISFACTION DATA")
print("=" * 80)

# Get count of satisfaction records
satisfaction_count = ChatbotFeedback.objects.filter(satisfaction_rating__isnull=False).count()
total_feedback = ChatbotFeedback.objects.all().count()

print(f"\nFound {total_feedback} total feedback entries")
print(f"Found {satisfaction_count} entries with satisfaction ratings")

# Option 1: Clear only satisfaction ratings (keep other feedback)
print("\nClearing satisfaction ratings from all feedback entries...")
ChatbotFeedback.objects.filter(satisfaction_rating__isnull=False).update(satisfaction_rating=None)

print(f"[SUCCESS] Cleared {satisfaction_count} satisfaction ratings")

# Verify
remaining = ChatbotFeedback.objects.filter(satisfaction_rating__isnull=False).count()
print(f"\nVerification: {remaining} satisfaction ratings remaining (should be 0)")

print("\n" + "=" * 80)
print("SCRIPT COMPLETED")
print("=" * 80)
print("\nAll satisfaction ratings have been removed from the database.")
print("Feedback entries are preserved but satisfaction ratings are cleared.")
print("=" * 80)
