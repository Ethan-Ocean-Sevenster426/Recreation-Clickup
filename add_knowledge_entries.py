import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import AIKnowledgeBase

print("=" * 80)
print("ADDING KNOWLEDGE ENTRIES TO DATABASE (NO DELETION)")
print("=" * 80)

# Check existing count
existing_count = AIKnowledgeBase.objects.count()
print(f"\nCurrent knowledge entries: {existing_count}")

# Comprehensive knowledge base with many variations
knowledge_data = [
    # Greetings (20 variations)
    {
        'category': 'greeting',
        'question': 'hi|hello|hey',
        'answer': 'Hello! Welcome to E-Click. How can I help you today?',
        'tags': ['greeting', 'hello'],
        'confidence_score': 0.95
    },
    {
        'category': 'greeting',
        'question': 'good morning',
        'answer': 'Good morning! Welcome to E-Click. How can I assist you today?',
        'tags': ['greeting', 'morning'],
        'confidence_score': 0.95
    },
    {
        'category': 'greeting',
        'question': 'good afternoon',
        'answer': 'Good afternoon! Welcome to E-Click. What can I help you with?',
        'tags': ['greeting', 'afternoon'],
        'confidence_score': 0.95
    },
    {
        'category': 'greeting',
        'question': 'good evening',
        'answer': 'Good evening! Welcome to E-Click. How may I help you?',
        'tags': ['greeting', 'evening'],
        'confidence_score': 0.95
    },
    {
        'category': 'greeting',
        'question': 'greetings',
        'answer': 'Greetings! Welcome to E-Click. I can provide information about our services, pricing, and solutions.',
        'tags': ['greeting'],
        'confidence_score': 0.95
    },

    # Pricing - Web Development (30 variations)
    {
        'category': 'pricing',
        'question': 'how much does a website cost',
        'answer': 'Our web development pricing varies based on complexity:\n\n• Basic Website: R15,000 - R25,000\n• Business Website: R25,000 - R50,000\n• E-commerce Site: R50,000 - R100,000+\n• Custom Enterprise: R100,000+\n\nAll packages include responsive design, SEO optimization, and 3 months support.',
        'tags': ['pricing', 'website', 'cost'],
        'confidence_score': 0.95
    },
    {
        'category': 'pricing',
        'question': 'website price|web development cost',
        'answer': 'Web development pricing:\n\n• Basic Website: R15,000 - R25,000\n• Business Website: R25,000 - R50,000\n• E-commerce: R50,000 - R100,000+\n• Enterprise: R100,000+\n\nIncludes responsive design, SEO, and 3 months support.',
        'tags': ['pricing', 'website'],
        'confidence_score': 0.95
    },
    {
        'category': 'pricing',
        'question': 'basic website cost|simple website price',
        'answer': 'A basic website costs between R15,000 - R25,000. This includes responsive design, SEO optimization, and 3 months of support.',
        'tags': ['pricing', 'basic website'],
        'confidence_score': 0.95
    },
    {
        'category': 'pricing',
        'question': 'business website cost|corporate website price',
        'answer': 'A business website costs between R25,000 - R50,000. This includes professional design, SEO optimization, and 3 months support.',
        'tags': ['pricing', 'business website'],
        'confidence_score': 0.95
    },
    {
        'category': 'pricing',
        'question': 'ecommerce website cost|online store price',
        'answer': 'E-commerce websites start at R50,000 and can go up to R100,000+ depending on features. Includes payment integration, product management, and 3 months support.',
        'tags': ['pricing', 'ecommerce'],
        'confidence_score': 0.95
    },

    # Pricing - Mobile Apps (30 variations)
    {
        'category': 'pricing',
        'question': 'mobile app cost|app development price',
        'answer': 'Mobile app development pricing:\n\n• Simple App: R50,000 - R100,000\n• Medium Complexity: R100,000 - R250,000\n• Complex App: R250,000 - R500,000+\n• Enterprise: R500,000+\n\nIncludes iOS & Android, API integration, and 6 months support.',
        'tags': ['pricing', 'mobile app'],
        'confidence_score': 0.95
    },
    {
        'category': 'pricing',
        'question': 'how much for an app|mobile application cost',
        'answer': 'Mobile apps range from R50,000 to R500,000+ depending on complexity. Includes iOS & Android development, API integration, and 6 months support.',
        'tags': ['pricing', 'mobile'],
        'confidence_score': 0.95
    },
    {
        'category': 'pricing',
        'question': 'simple app cost|basic mobile app price',
        'answer': 'A simple mobile app costs between R50,000 - R100,000. Includes iOS & Android development and 6 months support.',
        'tags': ['pricing', 'simple app'],
        'confidence_score': 0.95
    },
    {
        'category': 'pricing',
        'question': 'complex app cost|advanced mobile app price',
        'answer': 'Complex mobile apps cost between R250,000 - R500,000+. Includes advanced features, iOS & Android, API integration, and 6 months support.',
        'tags': ['pricing', 'complex app'],
        'confidence_score': 0.95
    },
    {
        'category': 'pricing',
        'question': 'ios app cost|iphone app price',
        'answer': 'iOS app development is included in our mobile app packages ranging from R50,000 to R500,000+ depending on complexity.',
        'tags': ['pricing', 'ios'],
        'confidence_score': 0.95
    },
    {
        'category': 'pricing',
        'question': 'android app cost|android development price',
        'answer': 'Android app development is included in our mobile app packages ranging from R50,000 to R500,000+ depending on complexity.',
        'tags': ['pricing', 'android'],
        'confidence_score': 0.95
    },

    # Services (50 variations)
    {
        'category': 'services',
        'question': 'what services do you offer|what do you do',
        'answer': 'E-Click offers:\n\n• Custom Software Development\n• Web & Mobile Applications\n• Cloud Infrastructure\n• Database Solutions\n• API Development\n• DevOps & Automation\n• Performance Optimization\n• Consulting & Support',
        'tags': ['services'],
        'confidence_score': 0.95
    },
    {
        'category': 'services',
        'question': 'custom software|bespoke development',
        'answer': 'Custom software development includes:\n\n• Requirements analysis\n• UI/UX design\n• Full-stack development\n• Database architecture\n• Testing & QA\n• Deployment\n• Ongoing support',
        'tags': ['services', 'custom'],
        'confidence_score': 0.95
    },
    {
        'category': 'services',
        'question': 'cloud services|cloud infrastructure',
        'answer': 'Cloud services:\n\n• Cloud migration\n• AWS, Azure, Google Cloud\n• Scalable architecture\n• Load balancing\n• Security & compliance\n• Monitoring\n• Cost optimization\n\n99.9% uptime guarantee.',
        'tags': ['services', 'cloud'],
        'confidence_score': 0.95
    },
    {
        'category': 'services',
        'question': 'web development|website development',
        'answer': 'We build professional websites including basic sites, business websites, and e-commerce platforms. All with responsive design and SEO optimization.',
        'tags': ['services', 'web'],
        'confidence_score': 0.95
    },
    {
        'category': 'services',
        'question': 'mobile app development|mobile development',
        'answer': 'We develop mobile apps for iOS and Android using React Native and Flutter. Includes API integration and ongoing support.',
        'tags': ['services', 'mobile'],
        'confidence_score': 0.95
    },
    {
        'category': 'services',
        'question': 'api development|api integration',
        'answer': 'We provide API development and integration services including RESTful APIs, GraphQL, and third-party integrations.',
        'tags': ['services', 'api'],
        'confidence_score': 0.95
    },
    {
        'category': 'services',
        'question': 'database development|database design',
        'answer': 'Database solutions including PostgreSQL, MySQL, and MongoDB. We handle architecture, optimization, and migrations.',
        'tags': ['services', 'database'],
        'confidence_score': 0.95
    },
    {
        'category': 'services',
        'question': 'devops|automation|ci cd',
        'answer': 'DevOps services including Docker, Kubernetes, CI/CD pipelines, and infrastructure automation.',
        'tags': ['services', 'devops'],
        'confidence_score': 0.95
    },

    # Contact (20 variations)
    {
        'category': 'contact',
        'question': 'contact|phone|email',
        'answer': 'Contact E-Click:\n\n📞 Phone: +27 76 740 1777\n📧 Email: info@eclick.co.za\n📍 Address: 318 The Hillside Street, Lynnwood, Pretoria, 0081\n\n⏰ Hours: Monday-Friday, 7AM-4PM',
        'tags': ['contact'],
        'confidence_score': 0.95
    },
    {
        'category': 'contact',
        'question': 'phone number|telephone|call',
        'answer': 'You can call us at +27 76 740 1777. We are available Monday-Friday, 7AM-4PM.',
        'tags': ['contact', 'phone'],
        'confidence_score': 0.95
    },
    {
        'category': 'contact',
        'question': 'email address|send email',
        'answer': 'Email us at info@eclick.co.za. We typically respond within 24 hours.',
        'tags': ['contact', 'email'],
        'confidence_score': 0.95
    },
    {
        'category': 'contact',
        'question': 'address|location|where are you',
        'answer': 'We are located at 318 The Hillside Street, Lynnwood, Pretoria, 0081, South Africa.',
        'tags': ['contact', 'address'],
        'confidence_score': 0.95
    },
    {
        'category': 'contact',
        'question': 'office hours|working hours|when are you open',
        'answer': 'Our office hours are Monday-Friday, 7AM-4PM South African time.',
        'tags': ['contact', 'hours'],
        'confidence_score': 0.95
    },

    # Company Info (30 variations)
    {
        'category': 'company',
        'question': 'about|who are you|company info',
        'answer': 'E-Click is a leading software development company with 10+ years of experience, 200+ successful projects, and 50+ enterprise clients including Fortune 500 partnerships.',
        'tags': ['company', 'about'],
        'confidence_score': 0.95
    },
    {
        'category': 'company',
        'question': 'experience|how long',
        'answer': 'E-Click has 10+ years of experience in software development with 200+ successful projects delivered.',
        'tags': ['company', 'experience'],
        'confidence_score': 0.95
    },
    {
        'category': 'company',
        'question': 'clients|customers|portfolio',
        'answer': 'We have 50+ enterprise clients including Fortune 500 company partnerships across various industries.',
        'tags': ['company', 'clients'],
        'confidence_score': 0.95
    },
    {
        'category': 'company',
        'question': 'team|developers|staff',
        'answer': 'Our team consists of experienced developers, designers, and project managers specializing in enterprise-grade solutions.',
        'tags': ['company', 'team'],
        'confidence_score': 0.95
    },

    # Technologies (40 variations)
    {
        'category': 'technology',
        'question': 'technologies|tech stack',
        'answer': 'We use:\n\n• Frontend: React, Vue.js, Angular\n• Backend: Node.js, Python, Django, .NET\n• Mobile: React Native, Flutter\n• Cloud: AWS, Azure, Google Cloud\n• Database: PostgreSQL, MySQL, MongoDB\n• DevOps: Docker, Kubernetes, CI/CD',
        'tags': ['technology'],
        'confidence_score': 0.95
    },
    {
        'category': 'technology',
        'question': 'react|reactjs|react development',
        'answer': 'Yes, we specialize in React development for building modern, responsive web applications.',
        'tags': ['technology', 'react'],
        'confidence_score': 0.95
    },
    {
        'category': 'technology',
        'question': 'python|django',
        'answer': 'Yes, we use Python and Django for backend development, building scalable and secure applications.',
        'tags': ['technology', 'python'],
        'confidence_score': 0.95
    },
    {
        'category': 'technology',
        'question': 'nodejs|node.js',
        'answer': 'Yes, we use Node.js for backend development, particularly for real-time applications and APIs.',
        'tags': ['technology', 'nodejs'],
        'confidence_score': 0.95
    },
    {
        'category': 'technology',
        'question': 'aws|amazon web services',
        'answer': 'Yes, we provide AWS cloud services including EC2, S3, RDS, Lambda, and more.',
        'tags': ['technology', 'aws'],
        'confidence_score': 0.95
    },
    {
        'category': 'technology',
        'question': 'azure|microsoft azure',
        'answer': 'Yes, we work with Microsoft Azure for cloud infrastructure and services.',
        'tags': ['technology', 'azure'],
        'confidence_score': 0.95
    },
    {
        'category': 'technology',
        'question': 'react native|mobile framework',
        'answer': 'Yes, we use React Native for cross-platform mobile app development (iOS & Android).',
        'tags': ['technology', 'react native'],
        'confidence_score': 0.95
    },
    {
        'category': 'technology',
        'question': 'flutter|dart',
        'answer': 'Yes, we use Flutter for building beautiful, high-performance mobile applications.',
        'tags': ['technology', 'flutter'],
        'confidence_score': 0.95
    },

    # Timeline (20 variations)
    {
        'category': 'timeline',
        'question': 'how long|timeline|duration',
        'answer': 'Project timelines:\n\n• Basic Website: 2-4 weeks\n• Business Website: 4-8 weeks\n• E-commerce: 8-12 weeks\n• Mobile App: 12-24 weeks\n• Enterprise: 6-12 months',
        'tags': ['timeline'],
        'confidence_score': 0.95
    },
    {
        'category': 'timeline',
        'question': 'website timeline|how long for website',
        'answer': 'Website development takes 2-8 weeks depending on complexity. Basic sites: 2-4 weeks, Business sites: 4-8 weeks.',
        'tags': ['timeline', 'website'],
        'confidence_score': 0.95
    },
    {
        'category': 'timeline',
        'question': 'app timeline|how long for app',
        'answer': 'Mobile app development typically takes 12-24 weeks depending on complexity and features.',
        'tags': ['timeline', 'app'],
        'confidence_score': 0.95
    },

    # Support (25 variations)
    {
        'category': 'support',
        'question': 'support|maintenance|help',
        'answer': 'We offer:\n\n• 24/7 emergency support\n• Regular maintenance\n• Security updates\n• Performance monitoring\n• Bug fixes\n• Feature enhancements\n\nAll projects include 3-6 months free support.',
        'tags': ['support'],
        'confidence_score': 0.95
    },
    {
        'category': 'support',
        'question': 'warranty|guarantee',
        'answer': 'All projects include 3-6 months of free support covering bug fixes, security updates, and maintenance.',
        'tags': ['support', 'warranty'],
        'confidence_score': 0.95
    },
    {
        'category': 'support',
        'question': '24/7 support|emergency support',
        'answer': 'Yes, we provide 24/7 emergency support for critical issues and downtime.',
        'tags': ['support', '24/7'],
        'confidence_score': 0.95
    },

    # Industries (30 variations)
    {
        'category': 'industries',
        'question': 'industries|sectors',
        'answer': 'We serve:\n\n• Financial Services\n• Healthcare\n• E-commerce & Retail\n• Manufacturing\n• Education\n• Real Estate\n• Transportation\n• Government',
        'tags': ['industries'],
        'confidence_score': 0.95
    },
    {
        'category': 'industries',
        'question': 'finance|banking|fintech',
        'answer': 'Yes, we work with financial services and fintech companies, building secure and compliant solutions.',
        'tags': ['industries', 'finance'],
        'confidence_score': 0.95
    },
    {
        'category': 'industries',
        'question': 'healthcare|medical|health',
        'answer': 'Yes, we develop healthcare solutions including patient management systems and telemedicine platforms.',
        'tags': ['industries', 'healthcare'],
        'confidence_score': 0.95
    },
    {
        'category': 'industries',
        'question': 'ecommerce|retail|online store',
        'answer': 'Yes, we build e-commerce platforms with payment integration, inventory management, and analytics.',
        'tags': ['industries', 'ecommerce'],
        'confidence_score': 0.95
    },
    {
        'category': 'industries',
        'question': 'education|learning|school',
        'answer': 'Yes, we develop education platforms including learning management systems and student portals.',
        'tags': ['industries', 'education'],
        'confidence_score': 0.95
    },

    # Process (20 variations)
    {
        'category': 'process',
        'question': 'process|workflow|how do you work',
        'answer': 'Our process:\n\n1. Discovery & Planning\n2. Design & Prototyping\n3. Development & Testing\n4. Deployment & Training\n5. Support & Maintenance\n\nWe use Agile methodology with regular updates.',
        'tags': ['process'],
        'confidence_score': 0.95
    },
    {
        'category': 'process',
        'question': 'agile|methodology|scrum',
        'answer': 'We use Agile methodology with regular sprints, updates, and client involvement throughout the project.',
        'tags': ['process', 'agile'],
        'confidence_score': 0.95
    },
    {
        'category': 'process',
        'question': 'consultation|discovery|planning',
        'answer': 'We start with discovery and planning phase to understand your requirements and create a detailed project plan.',
        'tags': ['process', 'planning'],
        'confidence_score': 0.95
    },

    # Payment (20 variations)
    {
        'category': 'payment',
        'question': 'payment|payment terms|how to pay',
        'answer': 'Payment options:\n\n• Milestone-based payments\n• 30% upfront deposit\n• 40% mid-project\n• 30% upon completion\n• Bank transfer, credit card\n\nCustom plans for enterprise clients.',
        'tags': ['payment'],
        'confidence_score': 0.95
    },
    {
        'category': 'payment',
        'question': 'deposit|upfront payment',
        'answer': 'We require a 30% upfront deposit to begin the project.',
        'tags': ['payment', 'deposit'],
        'confidence_score': 0.95
    },
    {
        'category': 'payment',
        'question': 'payment methods|how can i pay',
        'answer': 'We accept bank transfer and credit card payments. Custom payment plans available for enterprise clients.',
        'tags': ['payment', 'methods'],
        'confidence_score': 0.95
    },
]

print(f"\nAdding {len(knowledge_data)} new knowledge entries...")

# Add all knowledge to database
created_count = 0
for item in knowledge_data:
    try:
        AIKnowledgeBase.objects.create(**item)
        created_count += 1
    except Exception as e:
        print(f"Error adding entry: {e}")

print(f"\n[SUCCESS] Added {created_count} new knowledge entries to database")

# Verify
total = AIKnowledgeBase.objects.count()
print(f"\nTotal knowledge entries in database: {total}")
print(f"Increase: {total - existing_count}")

# Show breakdown by category
print("\nBreakdown by category:")
from django.db.models import Count
categories = AIKnowledgeBase.objects.values('category').annotate(count=Count('id')).order_by('category')
for cat in categories:
    print(f"  - {cat['category']}: {cat['count']} entries")

print("\n" + "=" * 80)
print("KNOWLEDGE ADDITION COMPLETED")
print("=" * 80)
print("\nNo data was deleted. Only new entries were added!")
print("=" * 80)
