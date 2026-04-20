#!/usr/bin/env python
"""Fix all pricing entries and add better variations"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import AIKnowledgeBase

pricing_answer = "Our pricing varies based on project scope, complexity, and requirements. We provide custom quotes tailored to your specific needs. Please contact us at info@eclick.co.za or call +27 76 740 1777 for a detailed estimate."

# Fix existing entries
fixes = [
    ('Pricing', pricing_answer, 'pricing'),
    ('Prices', pricing_answer, 'pricing'),
]

print("Fixing existing pricing entries...\n")
for question, answer, category in fixes:
    entry = AIKnowledgeBase.objects.filter(question=question).first()
    if entry:
        entry.answer = answer
        entry.category = category
        entry.save()
        print(f"Fixed: {question}")

# Add new variations
new_variations = [
    'I want to know your pricing',
    'Tell me about pricing',
    'Pricing information',
    'How much does it cost',
    'What do you charge',
    'I need a quote',
    'Can you give me a price',
    'Price list',
    'Pricing details',
    'Cost information',
]

print("\nAdding new pricing variations...\n")
for question in new_variations:
    # Check if it exists
    existing = AIKnowledgeBase.objects.filter(question=question).first()
    if not existing:
        AIKnowledgeBase.objects.create(
            question=question,
            answer=pricing_answer,
            category='pricing',
            tags=['pricing', 'cost', 'quote']
        )
        print(f"Added: {question}")
    else:
        print(f"Already exists: {question}")

print("\nDone! Pricing entries fixed and expanded.")
