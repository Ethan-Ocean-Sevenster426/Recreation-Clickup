#!/usr/bin/env python
"""Check pricing entries in AI knowledge base"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import AIKnowledgeBase

print("Searching for pricing-related entries...\n")

# Search for entries containing pricing keywords
pricing_keywords = ['pricing', 'price', 'cost', 'quote', 'rate']

for keyword in pricing_keywords:
    print(f"=== Entries with '{keyword}' ===")
    entries = AIKnowledgeBase.objects.filter(question__icontains=keyword)
    if entries:
        for entry in entries:
            print(f"\nQuestion: {entry.question}")
            print(f"Answer: {entry.answer[:100]}...")
            print(f"Category: {entry.category}")
    else:
        print(f"No entries found for '{keyword}'")
    print()

print("\n=== All pricing category entries ===")
pricing_cat = AIKnowledgeBase.objects.filter(category='pricing')
for entry in pricing_cat:
    print(f"\nQuestion: {entry.question}")
    print(f"Answer: {entry.answer}")
    print()
