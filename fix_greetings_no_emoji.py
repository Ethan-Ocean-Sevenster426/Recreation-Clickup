#!/usr/bin/env python
"""Update greeting responses without emojis"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import AIKnowledgeBase

# Update greeting responses to be shorter without emojis
greetings_updates = [
    {
        'question': 'Hi',
        'new_answer': 'Hi! How can I help you today?'
    },
    {
        'question': 'Hello',
        'new_answer': 'Hello! What can I help you with?'
    },
    {
        'question': 'Hey',
        'new_answer': 'Hey there! What would you like to know?'
    },
]

print("Updating greeting responses...\n")

for item in greetings_updates:
    try:
        entry = AIKnowledgeBase.objects.filter(question=item['question']).first()
        if entry:
            entry.answer = item['new_answer']
            entry.save()
            print(f"Updated: {item['question']}")
        else:
            print(f"Not found: {item['question']}")
    except Exception as e:
        print(f"Error: {item['question']} - {e}")

print("\nDone!")
