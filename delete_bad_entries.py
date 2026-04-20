#!/usr/bin/env python
"""Delete problematic entries causing wrong matches"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import AIKnowledgeBase

print("Deleting problematic entries...\n")

# Delete the bad "Automation" entry (ID 72)
try:
    bad_entry = AIKnowledgeBase.objects.get(id=72)
    print(f"Found bad entry:")
    print(f"  Question: {bad_entry.question}")
    print(f"  Answer: {bad_entry.answer[:60]}...")
    print(f"  Usage count: {bad_entry.usage_count}")
    bad_entry.delete()
    print("  DELETED!\n")
except AIKnowledgeBase.DoesNotExist:
    print("Entry ID 72 not found (may already be deleted)\n")

# Also check for and delete any entries with "contracts" that might confuse "contact"
contracts_entries = AIKnowledgeBase.objects.filter(
    question__iexact='contracts'
) | AIKnowledgeBase.objects.filter(
    question__iexact='contract'
)

if contracts_entries.exists():
    print("Found contract entries that might interfere:")
    for entry in contracts_entries:
        print(f"  ID: {entry.id}, Question: {entry.question}")
        entry.delete()
        print(f"    DELETED!")
else:
    print("No problematic contract entries found")

print("\nDone! Bad entries removed.")
print(f"Total entries remaining: {AIKnowledgeBase.objects.count()}")
