#!/usr/bin/env python
"""Update greeting responses to be more distinct from welcome message"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import AIKnowledgeBase

# Update greeting responses to be shorter and more distinct
greetings_updates = [
    {
        'question': 'Hi',
        'new_answer': 'Hi! 👋 How can I help you today?'
    },
    {
        'question': 'Hello',
        'new_answer': 'Hello! 👋 What can I help you with?'
    },
    {
        'question': 'Hey',
        'new_answer': 'Hey there! What would you like to know?'
    },
]

print("Updating greeting responses to be more concise...\n")

for item in greetings_updates:
    try:
        # Find the knowledge entry
        entry = AIKnowledgeBase.objects.filter(question=item['question']).first()
        if entry:
            old_answer = entry.answer
            entry.answer = item['new_answer']
            entry.save()
            print(f"[OK] Updated '{item['question']}'")
            print(f"  Old: {old_answer[:60]}...")
            print(f"  New: {item['new_answer']}\n")
        else:
            print(f"[SKIP] Entry not found for: {item['question']}\n")
    except Exception as e:
        print(f"[ERROR] Error updating '{item['question']}': {e}\n")

print("Greeting responses updated successfully!")
