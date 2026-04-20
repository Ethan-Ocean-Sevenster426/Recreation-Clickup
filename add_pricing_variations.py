#!/usr/bin/env python
"""Add more pricing question variations to improve AI matching"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.ai_service import ai_service

# Additional pricing variations
pricing_variations = [
    {
        'question': 'Pricing',
        'answer': 'Our pricing varies based on project scope, complexity, and requirements. We provide custom quotes tailored to your specific needs. Please contact us at info@eclick.co.za or call +27 76 740 1777 for a detailed estimate.',
        'category': 'pricing',
        'tags': ['price', 'pricing']
    },
    {
        'question': 'Prices',
        'answer': 'Our prices depend on your specific project needs. We offer competitive pricing tailored to each project. For a personalized quote, please contact us at info@eclick.co.za or call +27 76 740 1777.',
        'category': 'pricing',
        'tags': ['prices', 'cost']
    },
    {
        'question': 'Cost',
        'answer': 'Project costs vary based on scope and complexity. We provide custom quotes to match your budget and requirements. Reach out to us at info@eclick.co.za or +27 76 740 1777 for a detailed cost estimate.',
        'category': 'pricing',
        'tags': ['cost', 'pricing']
    },
    {
        'question': 'How much',
        'answer': 'Our pricing is customized based on your project requirements, scope, and timeline. We\'d be happy to provide a detailed quote. Contact us at info@eclick.co.za or call +27 76 740 1777 to discuss your needs.',
        'category': 'pricing',
        'tags': ['how much', 'cost', 'price']
    },
    {
        'question': 'Quote',
        'answer': 'We provide free, customized quotes for all our services. The cost depends on your specific project requirements. Contact us at info@eclick.co.za or call +27 76 740 1777 and we\'ll prepare a detailed quote for you.',
        'category': 'pricing',
        'tags': ['quote', 'estimate', 'pricing']
    },
    {
        'question': 'What are your rates',
        'answer': 'Our rates are competitive and vary based on project complexity and requirements. We offer flexible pricing models including fixed-price and hourly rates. Contact us at info@eclick.co.za or +27 76 740 1777 for specific rates.',
        'category': 'pricing',
        'tags': ['rates', 'pricing', 'cost']
    },
]

print("Adding pricing question variations...")
print(f"Total entries to add: {len(pricing_variations)}")

for idx, item in enumerate(pricing_variations, 1):
    ai_service.add_knowledge(
        question=item['question'],
        answer=item['answer'],
        category=item['category'],
        tags=item['tags']
    )
    print(f"  [{idx}/{len(pricing_variations)}] Added: {item['question']}")

print("\nPricing variations added successfully!")

# Show updated stats
stats = ai_service.get_learning_stats()
print(f"\nUpdated AI Stats:")
print(f"  - Knowledge Base Size: {stats['knowledge_base_size']}")
print(f"  - Total Conversations: {stats['total_conversations']}")
