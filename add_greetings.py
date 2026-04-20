#!/usr/bin/env python
"""Add greeting and conversational responses to the AI knowledge base"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.ai_service import ai_service

# Greetings and conversational knowledge
greetings_data = [
    {
        'question': 'Hi',
        'answer': 'Hello! Welcome to E-Click! I\'m here to help you learn about our software development services. What can I help you with today?',
        'category': 'greeting',
        'tags': ['greeting', 'hello', 'hi']
    },
    {
        'question': 'Hello',
        'answer': 'Hi there! Thanks for visiting E-Click. We specialize in custom software development, cloud solutions, and business automation. How can I assist you today?',
        'category': 'greeting',
        'tags': ['greeting', 'hello', 'hi']
    },
    {
        'question': 'Hey',
        'answer': 'Hey! Great to have you here. I\'m the E-Click assistant and I can help you with information about our services, pricing, contact details, and more. What would you like to know?',
        'category': 'greeting',
        'tags': ['greeting', 'hey']
    },
    {
        'question': 'Good morning',
        'answer': 'Good morning! Welcome to E-Click. How can I help you with your software development needs today?',
        'category': 'greeting',
        'tags': ['greeting', 'morning']
    },
    {
        'question': 'Good afternoon',
        'answer': 'Good afternoon! Thanks for reaching out. What can I tell you about E-Click\'s services today?',
        'category': 'greeting',
        'tags': ['greeting', 'afternoon']
    },
    {
        'question': 'I am looking at your website',
        'answer': 'Wonderful! I\'m glad you\'re interested in E-Click. We offer custom software development, mobile apps, cloud solutions, and business automation. Is there a specific service you\'d like to learn more about?',
        'category': 'conversation',
        'tags': ['browsing', 'looking', 'interested']
    },
    {
        'question': 'I am a potential client',
        'answer': 'That\'s great! We\'d love to work with you. E-Click specializes in building custom software solutions for businesses of all sizes. What kind of project are you considering?',
        'category': 'conversation',
        'tags': ['client', 'customer', 'potential']
    },
    {
        'question': 'I need help',
        'answer': 'I\'m here to help! You can ask me about our services, pricing, contact information, or any questions about E-Click. What do you need help with?',
        'category': 'conversation',
        'tags': ['help', 'assist', 'support']
    },
    {
        'question': 'Who are you',
        'answer': 'I\'m the E-Click AI assistant! I\'m here to help answer your questions about our software development services, pricing, contact details, and more. I can also help you connect with our team if you need personalized assistance.',
        'category': 'conversation',
        'tags': ['who', 'assistant', 'chatbot']
    },
    {
        'question': 'What can you do',
        'answer': 'I can help you with information about E-Click\'s services, pricing, contact details, business hours, our technology stack, and project process. I can also switch the website theme for you (try saying "dark mode" or "light mode") and collect your feedback!',
        'category': 'conversation',
        'tags': ['capabilities', 'features', 'what']
    },
    {
        'question': 'Goodbye',
        'answer': 'Goodbye! Thanks for chatting with me. If you need anything else, feel free to reach out at info@eclick.co.za or call us at +27 76 740 1777. Have a great day!',
        'category': 'farewell',
        'tags': ['goodbye', 'bye', 'farewell']
    },
    {
        'question': 'Thank you',
        'answer': 'You\'re very welcome! Happy to help. If you have any other questions about E-Click, just ask. Otherwise, feel free to contact us at info@eclick.co.za!',
        'category': 'gratitude',
        'tags': ['thanks', 'thank you']
    },
]

print("Adding greeting and conversational knowledge...")
print(f"Total entries to add: {len(greetings_data)}")

for idx, item in enumerate(greetings_data, 1):
    ai_service.add_knowledge(
        question=item['question'],
        answer=item['answer'],
        category=item['category'],
        tags=item['tags']
    )
    print(f"  [{idx}/{len(greetings_data)}] Added: {item['question']}")

print("\nGreeting knowledge added successfully!")

# Show updated stats
stats = ai_service.get_learning_stats()
print(f"\nUpdated AI Stats:")
print(f"  - Knowledge Base Size: {stats['knowledge_base_size']}")
print(f"  - Total Conversations: {stats['total_conversations']}")
