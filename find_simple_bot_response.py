import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import AIKnowledgeBase

# Search for the response the user is seeing
search_terms = [
    "simple bot",
    "limited knowledge",
    "contact our human team"
]

print("Searching for AI knowledge entries containing the problematic response...")
for term in search_terms:
    print(f"\n=== Searching for '{term}' ===")
    entries = AIKnowledgeBase.objects.filter(answer__icontains=term)
    print(f"Found {entries.count()} entries")
    for entry in entries[:3]:
        print(f"\nQ: {entry.question}")
        print(f"A: {entry.answer[:200]}")

# Also search for "hi" entries
print("\n\n=== Entries for 'hi' or 'hello' ===")
hi_entries = AIKnowledgeBase.objects.filter(question__iexact='hi') | AIKnowledgeBase.objects.filter(question__iexact='hello')
for entry in hi_entries:
    print(f"\nQ: {entry.question}")
    print(f"A: {entry.answer}")
