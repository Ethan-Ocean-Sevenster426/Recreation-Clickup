#!/usr/bin/env python
"""Fix pricing entry and update satisfaction timing"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import AIKnowledgeBase

# Fix the pricing entry
try:
    pricing_entry = AIKnowledgeBase.objects.get(question='Pricing')
    pricing_entry.answer = 'Our pricing varies based on project scope, complexity, and requirements. We provide custom quotes tailored to your specific needs. Please contact us at info@eclick.co.za or call +27 76 740 1777 for a detailed estimate.'
    pricing_entry.save()
    print("✓ Fixed 'Pricing' entry")
except AIKnowledgeBase.DoesNotExist:
    print("✗ Pricing entry not found")

# Add more pricing variations to ensure good matching
from home.ai_service import ai_service

pricing_fixes = [
    {
        'question': 'What does it cost',
        'answer': 'Our costs vary based on your project requirements. We provide customized quotes. Contact us at info@eclick.co.za or +27 76 740 1777 for a detailed estimate.',
        'category': 'pricing',
        'tags': ['cost', 'pricing', 'price']
    },
    {
        'question': 'Price list',
        'answer': 'We don\'t have a fixed price list as every project is unique. We provide custom quotes based on your specific needs. Contact us at info@eclick.co.za or +27 76 740 1777.',
        'category': 'pricing',
        'tags': ['price', 'list', 'pricing']
    },
    {
        'question': 'Budget',
        'answer': 'We work with various budgets and can tailor our services to fit yours. Contact us at info@eclick.co.za or +27 76 740 1777 to discuss your budget and requirements.',
        'category': 'pricing',
        'tags': ['budget', 'cost']
    },
]

for item in pricing_fixes:
    ai_service.add_knowledge(
        question=item['question'],
        answer=item['answer'],
        category=item['category'],
        tags=item['tags']
    )
    print(f"✓ Added: {item['question']}")

print("\n✓ All pricing entries fixed!")
