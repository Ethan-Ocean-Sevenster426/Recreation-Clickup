import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import AIKnowledgeBase

print("=" * 80)
print("REMOVING PRICING INFO AND ADDING CONTACT RESPONSES")
print("=" * 80)

# Delete all pricing-related entries
deleted = AIKnowledgeBase.objects.filter(category='pricing').delete()
print(f"\nDeleted {deleted[0]} pricing entries")

# Add new responses that direct to contact
contact_pricing_entries = [
    {
        'category': 'pricing',
        'question': 'price|pricing|cost|how much|quote|estimate',
        'answer': 'For accurate pricing information tailored to your specific needs, please contact our team:\n\n📞 Phone: +27 76 740 1777\n📧 Email: info@eclick.co.za\n\nOur team will provide you with a detailed quote based on your requirements.',
        'tags': ['pricing', 'contact'],
        'confidence_score': 0.95
    },
    {
        'category': 'pricing',
        'question': 'website cost|web development price|how much website',
        'answer': 'For a customized quote on web development, please reach out to our team:\n\n📞 +27 76 740 1777\n📧 info@eclick.co.za\n\nWe\'ll discuss your requirements and provide accurate pricing.',
        'tags': ['pricing', 'website', 'contact'],
        'confidence_score': 0.95
    },
    {
        'category': 'pricing',
        'question': 'app cost|mobile app price|application price',
        'answer': 'For mobile app pricing details, please contact us:\n\n📞 +27 76 740 1777\n📧 info@eclick.co.za\n\nOur team will assess your needs and provide a detailed estimate.',
        'tags': ['pricing', 'mobile', 'contact'],
        'confidence_score': 0.95
    }
]

created = 0
for entry in contact_pricing_entries:
    AIKnowledgeBase.objects.create(**entry)
    created += 1

print(f"Added {created} new contact-based pricing responses")
print("\n" + "=" * 80)
print("COMPLETED - All pricing now directs to contact team")
print("=" * 80)
