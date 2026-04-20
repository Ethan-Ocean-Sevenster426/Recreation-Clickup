import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import AIKnowledgeBase

print("=" * 80)
print("SYNCING CHATBOT KNOWLEDGE TO DATABASE")
print("=" * 80)

# Clear existing knowledge
existing_count = AIKnowledgeBase.objects.count()
print(f"\nFound {existing_count} existing knowledge entries")
AIKnowledgeBase.objects.all().delete()
print("Cleared all existing knowledge")

# Add comprehensive knowledge base
knowledge_data = [
    # Greetings
    {
        'category': 'greeting',
        'question': 'hi|hello|hey|good morning|good afternoon|good evening|greetings',
        'answer': 'Hello! Welcome to E-Click. How can I help you today? I can provide information about our services, pricing, and solutions.',
        'tags': ['greeting', 'hello', 'hi'],
        'confidence_score': 0.95
    },

    # Pricing - Web Development
    {
        'category': 'pricing',
        'question': 'how much does a website cost|website price|web development cost|website pricing',
        'answer': 'Our web development pricing varies based on complexity:\n\n• Basic Website: R15,000 - R25,000\n• Business Website: R25,000 - R50,000\n• E-commerce Site: R50,000 - R100,000+\n• Custom Enterprise: R100,000+\n\nAll packages include responsive design, SEO optimization, and 3 months support.',
        'tags': ['pricing', 'website', 'cost', 'web development'],
        'confidence_score': 0.95
    },

    # Pricing - Mobile Apps
    {
        'category': 'pricing',
        'question': 'mobile app cost|app development price|how much for an app',
        'answer': 'Mobile app development pricing:\n\n• Simple App: R50,000 - R100,000\n• Medium Complexity: R100,000 - R250,000\n• Complex App: R250,000 - R500,000+\n• Enterprise Solution: R500,000+\n\nIncludes iOS & Android development, API integration, and 6 months support.',
        'tags': ['pricing', 'mobile app', 'cost'],
        'confidence_score': 0.95
    },

    # Services - General
    {
        'category': 'services',
        'question': 'what services do you offer|what do you do|services',
        'answer': 'E-Click offers comprehensive software solutions:\n\n• Custom Software Development\n• Web & Mobile Applications\n• Cloud Infrastructure\n• Database Solutions\n• API Development\n• DevOps & Automation\n• Performance Optimization\n• Consulting & Support\n\nWe specialize in enterprise-grade solutions.',
        'tags': ['services', 'offerings'],
        'confidence_score': 0.95
    },

    # Services - Custom Development
    {
        'category': 'services',
        'question': 'custom software|bespoke development|tailored solution',
        'answer': 'Our custom software development service includes:\n\n• Requirements analysis & planning\n• UI/UX design\n• Full-stack development\n• Database architecture\n• Testing & QA\n• Deployment & training\n• Ongoing support\n\nWe build solutions tailored to your exact business needs.',
        'tags': ['custom development', 'bespoke software'],
        'confidence_score': 0.95
    },

    # Services - Cloud
    {
        'category': 'services',
        'question': 'cloud services|cloud infrastructure|aws|azure',
        'answer': 'Our cloud infrastructure services:\n\n• Cloud migration & setup\n• AWS, Azure, Google Cloud\n• Scalable architecture design\n• Load balancing & auto-scaling\n• Security & compliance\n• Monitoring & maintenance\n• Cost optimization\n\n99.9% uptime guarantee.',
        'tags': ['cloud', 'infrastructure', 'aws', 'azure'],
        'confidence_score': 0.95
    },

    # Contact Information
    {
        'category': 'contact',
        'question': 'contact|phone|email|address|location',
        'answer': 'Contact E-Click:\n\n📞 Phone: +27 76 740 1777\n📧 Email: info@eclick.co.za\n📍 Address: 318 The Hillside Street, Lynnwood, Pretoria, 0081\n\n⏰ Hours: Monday-Friday, 7AM-4PM\n\nFeel free to reach out anytime!',
        'tags': ['contact', 'phone', 'email', 'address'],
        'confidence_score': 0.95
    },

    # Company Info
    {
        'category': 'company',
        'question': 'about|who are you|company info|experience',
        'answer': 'E-Click is a leading software development company with:\n\n• 10+ years of experience\n• 200+ successful projects\n• 50+ enterprise clients\n• Fortune 500 company partnerships\n\nWe specialize in delivering innovative, enterprise-grade software solutions that help businesses grow and succeed.',
        'tags': ['about', 'company', 'experience'],
        'confidence_score': 0.95
    },

    # Technologies
    {
        'category': 'technology',
        'question': 'technologies|tech stack|programming languages|frameworks',
        'answer': 'We work with cutting-edge technologies:\n\n• Frontend: React, Vue.js, Angular\n• Backend: Node.js, Python, Django, .NET\n• Mobile: React Native, Flutter\n• Cloud: AWS, Azure, Google Cloud\n• Database: PostgreSQL, MySQL, MongoDB\n• DevOps: Docker, Kubernetes, CI/CD\n\nWe choose the best tech for your needs.',
        'tags': ['technology', 'tech stack', 'programming'],
        'confidence_score': 0.95
    },

    # Timeline
    {
        'category': 'timeline',
        'question': 'how long|timeline|duration|project time',
        'answer': 'Project timelines vary by complexity:\n\n• Basic Website: 2-4 weeks\n• Business Website: 4-8 weeks\n• E-commerce: 8-12 weeks\n• Mobile App: 12-24 weeks\n• Enterprise Solution: 6-12 months\n\nWe provide detailed timelines during consultation.',
        'tags': ['timeline', 'duration'],
        'confidence_score': 0.95
    },

    # Support
    {
        'category': 'support',
        'question': 'support|maintenance|help after launch|post-launch',
        'answer': 'We offer comprehensive support:\n\n• 24/7 emergency support\n• Regular maintenance\n• Security updates\n• Performance monitoring\n• Bug fixes\n• Feature enhancements\n• Training & documentation\n\nAll projects include 3-6 months free support.',
        'tags': ['support', 'maintenance', 'post-launch'],
        'confidence_score': 0.95
    },

    # Industries
    {
        'category': 'industries',
        'question': 'industries|sectors|who do you work with',
        'answer': 'We serve diverse industries:\n\n• Financial Services\n• Healthcare\n• E-commerce & Retail\n• Manufacturing\n• Education\n• Real Estate\n• Transportation & Logistics\n• Government\n\nOur solutions are customized for each sector.',
        'tags': ['industries', 'sectors', 'clients'],
        'confidence_score': 0.95
    },

    # Process
    {
        'category': 'process',
        'question': 'process|workflow|how do you work|methodology',
        'answer': 'Our development process:\n\n1. Discovery & Planning\n2. Design & Prototyping\n3. Development & Testing\n4. Deployment & Training\n5. Support & Maintenance\n\nWe use Agile methodology with regular updates and client involvement.',
        'tags': ['process', 'workflow', 'methodology'],
        'confidence_score': 0.95
    },

    # Payment
    {
        'category': 'payment',
        'question': 'payment|payment terms|how to pay|invoice',
        'answer': 'Flexible payment options:\n\n• Milestone-based payments\n• 30% upfront deposit\n• 40% mid-project\n• 30% upon completion\n• Monthly retainers available\n• Bank transfer, credit card\n\nCustom payment plans for enterprise clients.',
        'tags': ['payment', 'terms', 'invoice'],
        'confidence_score': 0.95
    },
]

# Add all knowledge to database
created_count = 0
for item in knowledge_data:
    AIKnowledgeBase.objects.create(**item)
    created_count += 1

print(f"\n[SUCCESS] Added {created_count} knowledge entries to database")

# Verify
total = AIKnowledgeBase.objects.count()
print(f"\nVerification: {total} total knowledge entries in database")

# Show breakdown by category
print("\nBreakdown by category:")
from django.db.models import Count
categories = AIKnowledgeBase.objects.values('category').annotate(count=Count('id')).order_by('category')
for cat in categories:
    print(f"  - {cat['category']}: {cat['count']} entries")

print("\n" + "=" * 80)
print("SYNC COMPLETED")
print("=" * 80)
print("\nThe chatbot should now respond with proper pricing and service information!")
print("=" * 80)
