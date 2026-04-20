#!/usr/bin/env python
"""
Initialize AI Knowledge Base with E-Click company information
Run this script to populate the chatbot with intelligent responses
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.ai_service import ai_service

# Company knowledge base
knowledge_data = [
    # Services
    {
        'question': 'What services does E-Click offer?',
        'answer': 'E-Click offers custom software development, cloud solutions, business automation, enterprise integration, and technical consultancy services. We specialize in building tailored solutions for businesses of all sizes.',
        'category': 'services',
        'tags': ['services', 'offerings', 'what we do']
    },
    {
        'question': 'What is business automation?',
        'answer': 'Our business automation services help streamline your workflows, reduce manual tasks, and increase efficiency through intelligent process automation. We digitize business processes to save time and reduce errors.',
        'category': 'services',
        'tags': ['automation', 'workflow', 'process']
    },
    {
        'question': 'Do you build mobile apps?',
        'answer': 'Yes! We develop custom mobile applications for both iOS and Android platforms. Our team creates user-friendly, high-performance mobile solutions tailored to your business needs.',
        'category': 'services',
        'tags': ['mobile', 'apps', 'development']
    },
    {
        'question': 'Do you offer cloud solutions?',
        'answer': 'Absolutely! We provide cloud infrastructure setup, migration, and management services. We work with major cloud providers to help businesses leverage cloud computing for scalability and cost-efficiency.',
        'category': 'services',
        'tags': ['cloud', 'infrastructure', 'hosting']
    },

    # Contact Information
    {
        'question': 'How can I contact E-Click?',
        'answer': 'You can reach us through our contact form on this website, by email at info@eclick.co.za, or by phone at +27 76 740 1777. Our team is available Monday to Friday, 7AM-4PM.',
        'category': 'contact',
        'tags': ['contact', 'email', 'phone', 'reach us']
    },
    {
        'question': 'What is your email address?',
        'answer': 'You can email us at info@eclick.co.za. We typically respond within 24 hours during business days.',
        'category': 'contact',
        'tags': ['email', 'contact']
    },
    {
        'question': 'What is your phone number?',
        'answer': 'You can call us at +27 76 740 1777. Our business hours are Monday to Friday, 7AM-4PM South African time.',
        'category': 'contact',
        'tags': ['phone', 'call', 'telephone']
    },
    {
        'question': 'What are your business hours?',
        'answer': 'We\'re available Monday to Friday, 7AM-4PM South African time. For urgent matters outside these hours, please email us at info@eclick.co.za and we\'ll respond as soon as possible.',
        'category': 'contact',
        'tags': ['hours', 'availability', 'when']
    },

    # Pricing
    {
        'question': 'How much do your services cost?',
        'answer': 'Our pricing varies based on project scope, complexity, and requirements. We provide custom quotes tailored to your specific needs. Please contact us at info@eclick.co.za for a detailed estimate.',
        'category': 'pricing',
        'tags': ['price', 'cost', 'pricing', 'how much']
    },
    {
        'question': 'Do you offer free consultations?',
        'answer': 'Yes! We offer free initial consultations to understand your needs and discuss how we can help. Contact us to schedule a consultation.',
        'category': 'pricing',
        'tags': ['consultation', 'free', 'meeting']
    },

    # Company Information
    {
        'question': 'What is E-Click?',
        'answer': 'E-Click is a software development company specializing in custom digital solutions. We help businesses transform their ideas into powerful software applications, from web platforms to mobile apps and automation systems.',
        'category': 'company',
        'tags': ['about', 'company', 'who we are']
    },
    {
        'question': 'Where is E-Click located?',
        'answer': 'E-Click is based in South Africa. We serve clients locally and internationally, with expertise in remote collaboration and project delivery.',
        'category': 'company',
        'tags': ['location', 'where', 'address']
    },
    {
        'question': 'How long has E-Click been in business?',
        'answer': 'E-Click has been providing software development services to businesses across various industries. Our team brings years of combined experience in software engineering and digital transformation.',
        'category': 'company',
        'tags': ['history', 'experience', 'years']
    },

    # Technical
    {
        'question': 'What technologies do you use?',
        'answer': 'We work with modern technologies including Python, Django, React, JavaScript, Node.js, cloud platforms (AWS, Azure, Google Cloud), and more. We choose the best technology stack for each project based on your specific requirements.',
        'category': 'technical',
        'tags': ['technology', 'tech stack', 'programming']
    },
    {
        'question': 'Do you offer website development?',
        'answer': 'Yes! We build custom websites and web applications using modern technologies. From corporate websites to complex web platforms, we create responsive, fast, and secure solutions.',
        'category': 'services',
        'tags': ['website', 'web development', 'web app']
    },
    {
        'question': 'Can you help with database design?',
        'answer': 'Absolutely! We provide database design, optimization, and management services. We work with SQL and NoSQL databases to ensure your data is structured efficiently and securely.',
        'category': 'services',
        'tags': ['database', 'data', 'SQL']
    },

    # Process
    {
        'question': 'How do you work with clients?',
        'answer': 'We follow an agile development approach with regular communication and feedback. Projects typically start with a consultation, followed by planning, development in iterative sprints, testing, and deployment. We keep you involved throughout the process.',
        'category': 'process',
        'tags': ['workflow', 'methodology', 'how we work']
    },
    {
        'question': 'Do you provide support after launch?',
        'answer': 'Yes! We offer ongoing maintenance and support services to ensure your application runs smoothly. We can provide bug fixes, updates, and enhancements as needed.',
        'category': 'services',
        'tags': ['support', 'maintenance', 'after launch']
    },
    {
        'question': 'How long does a typical project take?',
        'answer': 'Project timelines vary based on scope and complexity. Simple websites might take 2-4 weeks, while complex applications can take several months. We provide detailed timeline estimates during the planning phase.',
        'category': 'process',
        'tags': ['timeline', 'duration', 'how long']
    },

    # Common Queries
    {
        'question': 'Can you integrate with existing systems?',
        'answer': 'Yes! We specialize in system integration and can connect your new solution with existing software, databases, APIs, and third-party services. We ensure seamless data flow between systems.',
        'category': 'services',
        'tags': ['integration', 'API', 'connect']
    },
    {
        'question': 'Do you work with startups?',
        'answer': 'Absolutely! We work with businesses of all sizes, from startups to enterprises. We understand the unique challenges startups face and can help bring your MVP to market efficiently.',
        'category': 'company',
        'tags': ['startup', 'small business', 'entrepreneur']
    },
    {
        'question': 'Is my data secure?',
        'answer': 'Yes, security is a top priority. We implement industry-standard security practices including encryption, secure authentication, regular security audits, and compliance with data protection regulations.',
        'category': 'technical',
        'tags': ['security', 'data protection', 'safe']
    },
]

def initialize():
    """Initialize the knowledge base"""
    print("Initializing AI Knowledge Base for E-Click Chatbot...")
    print(f"Adding {len(knowledge_data)} knowledge entries...")

    for idx, item in enumerate(knowledge_data, 1):
        ai_service.add_knowledge(
            question=item['question'],
            answer=item['answer'],
            category=item['category'],
            tags=item['tags']
        )
        print(f"  [{idx}/{len(knowledge_data)}] Added: {item['question'][:50]}...")

    print("\n✓ Knowledge base initialized successfully!")
    print(f"✓ Total entries: {len(knowledge_data)}")
    print("\nThe chatbot is now ready with intelligent responses about E-Click services.")

    # Show stats
    stats = ai_service.get_learning_stats()
    print(f"\nCurrent AI Stats:")
    print(f"  - Knowledge Base Size: {stats['knowledge_base_size']}")
    print(f"  - Total Conversations: {stats['total_conversations']}")

if __name__ == '__main__':
    initialize()
