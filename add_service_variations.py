#!/usr/bin/env python
"""Add service question variations for better AI matching"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.ai_service import ai_service

# Service variations
service_variations = [
    {
        'question': 'Services',
        'answer': 'E-Click offers custom software development, mobile apps, cloud solutions, business automation, database design, API development, and technical consultancy. What specific service are you interested in?',
        'category': 'services',
        'tags': ['services', 'offerings']
    },
    {
        'question': 'What do you do',
        'answer': 'We build custom software solutions for businesses. This includes web applications, mobile apps, cloud infrastructure, automation systems, and integration services. How can we help with your project?',
        'category': 'services',
        'tags': ['services', 'what', 'do']
    },
    {
        'question': 'Offerings',
        'answer': 'Our main offerings include custom software development, mobile app development, cloud solutions, business process automation, database architecture, API development, and ongoing technical support.',
        'category': 'services',
        'tags': ['offerings', 'services']
    },
    {
        'question': 'Contact',
        'answer': 'You can reach us at info@eclick.co.za or call +27 76 740 1777. We\'re available Monday to Friday, 7AM-4PM. Feel free to use our contact form as well!',
        'category': 'contact',
        'tags': ['contact']
    },
    {
        'question': 'Email',
        'answer': 'Our email address is info@eclick.co.za. We typically respond within 24 hours during business days.',
        'category': 'contact',
        'tags': ['email', 'contact']
    },
    {
        'question': 'Phone',
        'answer': 'You can call us at +27 76 740 1777. Our business hours are Monday to Friday, 7AM-4PM South African time.',
        'category': 'contact',
        'tags': ['phone', 'call']
    },
    {
        'question': 'Hours',
        'answer': 'We\'re available Monday to Friday, 7AM-4PM South African time. For urgent matters outside these hours, please email info@eclick.co.za.',
        'category': 'contact',
        'tags': ['hours', 'time']
    },
]

print("Adding service and contact variations...")
print(f"Total entries to add: {len(service_variations)}")

for idx, item in enumerate(service_variations, 1):
    ai_service.add_knowledge(
        question=item['question'],
        answer=item['answer'],
        category=item['category'],
        tags=item['tags']
    )
    print(f"  [{idx}/{len(service_variations)}] Added: {item['question']}")

print("\nService variations added successfully!")

# Show updated stats
stats = ai_service.get_learning_stats()
print(f"\nUpdated AI Stats:")
print(f"  - Knowledge Base Size: {stats['knowledge_base_size']}")
print(f"  - Total Conversations: {stats['total_conversations']}")
