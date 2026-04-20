#!/usr/bin/env python
"""Find the workshops/requirements entry"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import AIKnowledgeBase

print("Searching for workshops/requirements entry...\n")

# Search for entries containing the wrong answer
entries = AIKnowledgeBase.objects.filter(answer__icontains='workshops')
if entries:
    for entry in entries:
        print(f"Question: {entry.question}")
        print(f"Answer: {entry.answer}")
        print(f"Category: {entry.category}")
        print(f"Tags: {entry.tags}")
        print()
else:
    print("No entries found with 'workshops'")
