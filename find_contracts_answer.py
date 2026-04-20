#!/usr/bin/env python
"""Find entry with 'flexible contracts' answer"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import AIKnowledgeBase

print("Finding entries with 'flexible contracts' or 'contracts' in answer...\n")

# Search for entries with contracts in the answer
entries = AIKnowledgeBase.objects.filter(answer__icontains='contracts')
if entries:
    for entry in entries:
        print(f"ID: {entry.id}")
        print(f"Question: {entry.question}")
        print(f"Answer: {entry.answer}")
        print(f"Usage count: {entry.usage_count}")
        print(f"Category: {entry.category}")
        print()
else:
    print("No entries found with 'contracts' in answer")
