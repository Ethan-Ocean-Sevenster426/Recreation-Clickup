#!/usr/bin/env python
"""Find problematic entries causing wrong matches"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import AIKnowledgeBase

print("Finding problematic entries...\n")

# Find entries with "contract" (not "contact")
print("=== Entries with 'contract' ===")
contracts = AIKnowledgeBase.objects.filter(question__icontains='contract')
for entry in contracts:
    print(f"ID: {entry.id}")
    print(f"Question: {entry.question}")
    print(f"Answer: {entry.answer[:80]}...")
    print(f"Usage count: {entry.usage_count}")
    print()

# Find the automation/workshops entry
print("\n=== Entries with 'automation' ===")
automation = AIKnowledgeBase.objects.filter(question__icontains='automation')
for entry in automation:
    print(f"ID: {entry.id}")
    print(f"Question: {entry.question}")
    print(f"Answer: {entry.answer[:80]}...")
    print(f"Usage count: {entry.usage_count}")
    print()

# Find entries with workshops
print("\n=== Entries with 'workshops' in answer ===")
workshops = AIKnowledgeBase.objects.filter(answer__icontains='workshops')
for entry in workshops:
    print(f"ID: {entry.id}")
    print(f"Question: {entry.question}")
    print(f"Answer: {entry.answer[:80]}...")
    print(f"Usage count: {entry.usage_count}")
    print()
