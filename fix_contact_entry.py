#!/usr/bin/env python
"""Fix the Contact entry that has wrong answer about contracts"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import AIKnowledgeBase

print("Fixing Contact entry...\n")

contact_response = "You can reach us at info@eclick.co.za or call +27 76 740 1777. We're available Monday to Friday, 7AM-4PM South African time."

try:
    # Fix entry ID 41
    entry = AIKnowledgeBase.objects.get(id=41)
    print(f"Found entry ID 41:")
    print(f"  Question: {entry.question}")
    print(f"  Old Answer: {entry.answer}")
    print(f"  Category: {entry.category}")

    entry.answer = contact_response
    entry.category = 'contact'
    entry.tags = ['contact', 'info']
    entry.save()

    print(f"\n  Updated to:")
    print(f"  New Answer: {entry.answer}")
    print(f"  New Category: {entry.category}")
    print(f"  FIXED!\n")
except AIKnowledgeBase.DoesNotExist:
    print("Entry ID 41 not found\n")

print("Done!")
