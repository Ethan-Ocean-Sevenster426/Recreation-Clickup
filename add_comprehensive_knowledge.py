#!/usr/bin/env python
"""Add comprehensive knowledge base covering all aspects of software development"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.ai_service import ai_service

# Comprehensive knowledge base
comprehensive_knowledge = [
    # ==== WEB DEVELOPMENT ====
    {'question': 'Web development', 'answer': 'We build custom websites and web applications using modern technologies like React, Django, Node.js, and more. From simple corporate sites to complex web platforms.', 'category': 'web', 'tags': ['web', 'development']},
    {'question': 'Website', 'answer': 'We create professional, responsive websites tailored to your business needs. Our sites are fast, secure, and optimized for all devices.', 'category': 'web', 'tags': ['website']},
    {'question': 'Web app', 'answer': 'We develop custom web applications with advanced functionality including user authentication, databases, APIs, and real-time features.', 'category': 'web', 'tags': ['web app', 'application']},
    {'question': 'E-commerce', 'answer': 'We build e-commerce platforms with shopping carts, payment processing, inventory management, and order tracking. Scalable solutions for online retail.', 'category': 'web', 'tags': ['ecommerce', 'shopping', 'online store']},
    {'question': 'Responsive design', 'answer': 'All our websites are responsive, meaning they work perfectly on desktop, tablet, and mobile devices. We prioritize mobile-first design.', 'category': 'web', 'tags': ['responsive', 'mobile', 'design']},
    {'question': 'React', 'answer': 'We use React for building modern, interactive user interfaces. React provides fast performance and excellent user experience.', 'category': 'tech', 'tags': ['react', 'frontend']},
    {'question': 'Django', 'answer': 'Django is our primary Python framework for backend development. It\'s powerful, secure, and perfect for complex web applications.', 'category': 'tech', 'tags': ['django', 'python', 'backend']},

    # ==== MOBILE APPS ====
    {'question': 'Mobile', 'answer': 'We develop native and cross-platform mobile apps for iOS and Android. From concept to deployment on app stores.', 'category': 'mobile', 'tags': ['mobile', 'app']},
    {'question': 'iOS app', 'answer': 'We build native iOS applications using Swift and SwiftUI, optimized for iPhone and iPad with Apple\'s latest technologies.', 'category': 'mobile', 'tags': ['ios', 'iphone', 'apple']},
    {'question': 'Android app', 'answer': 'Our Android apps are built using Kotlin and Java, designed to work across the entire Android ecosystem from phones to tablets.', 'category': 'mobile', 'tags': ['android', 'google']},
    {'question': 'Cross-platform', 'answer': 'We develop cross-platform apps using React Native or Flutter, allowing one codebase to run on both iOS and Android.', 'category': 'mobile', 'tags': ['cross-platform', 'react native', 'flutter']},
    {'question': 'App store', 'answer': 'We handle the complete app store submission process for both Apple App Store and Google Play Store, including guidelines compliance.', 'category': 'mobile', 'tags': ['app store', 'submission']},

    # ==== CLOUD & INFRASTRUCTURE ====
    {'question': 'Cloud', 'answer': 'We provide cloud infrastructure setup, migration, and management on AWS, Azure, and Google Cloud Platform for scalability and reliability.', 'category': 'cloud', 'tags': ['cloud', 'infrastructure']},
    {'question': 'AWS', 'answer': 'We work with Amazon Web Services (AWS) including EC2, S3, RDS, Lambda, and more to build scalable cloud solutions.', 'category': 'cloud', 'tags': ['aws', 'amazon']},
    {'question': 'Azure', 'answer': 'Microsoft Azure cloud services including virtual machines, app services, and databases. Perfect for enterprise integrations.', 'category': 'cloud', 'tags': ['azure', 'microsoft']},
    {'question': 'Google Cloud', 'answer': 'We deploy applications on Google Cloud Platform using Compute Engine, Cloud Storage, and other GCP services.', 'category': 'cloud', 'tags': ['gcp', 'google cloud']},
    {'question': 'Hosting', 'answer': 'We provide managed hosting solutions with 99.9% uptime, automatic backups, security monitoring, and 24/7 support.', 'category': 'cloud', 'tags': ['hosting', 'server']},
    {'question': 'Server', 'answer': 'We set up and manage dedicated servers, VPS, and cloud servers with optimal configuration for your application needs.', 'category': 'cloud', 'tags': ['server', 'vps']},
    {'question': 'DevOps', 'answer': 'Our DevOps services include CI/CD pipelines, automated testing, deployment automation, and infrastructure as code.', 'category': 'cloud', 'tags': ['devops', 'automation']},

    # ==== DATABASE ====
    {'question': 'Database', 'answer': 'We design, optimize, and manage databases including PostgreSQL, MySQL, MongoDB, and Redis for efficient data storage and retrieval.', 'category': 'database', 'tags': ['database', 'data']},
    {'question': 'SQL', 'answer': 'We work with SQL databases like PostgreSQL and MySQL for relational data with complex queries and transactions.', 'category': 'database', 'tags': ['sql', 'postgresql', 'mysql']},
    {'question': 'MongoDB', 'answer': 'MongoDB is our choice for NoSQL document databases, perfect for flexible schemas and large-scale data.', 'category': 'database', 'tags': ['mongodb', 'nosql']},
    {'question': 'Data migration', 'answer': 'We handle data migration from legacy systems to modern databases with zero data loss and minimal downtime.', 'category': 'database', 'tags': ['migration', 'data']},

    # ==== API & INTEGRATION ====
    {'question': 'API', 'answer': 'We develop RESTful and GraphQL APIs for seamless integration between systems, mobile apps, and third-party services.', 'category': 'api', 'tags': ['api', 'rest', 'graphql']},
    {'question': 'Integration', 'answer': 'We integrate your software with existing systems, third-party APIs, payment gateways, and external services.', 'category': 'api', 'tags': ['integration', 'connect']},
    {'question': 'REST API', 'answer': 'We build RESTful APIs following best practices with proper authentication, rate limiting, and documentation.', 'category': 'api', 'tags': ['rest', 'api']},
    {'question': 'Payment gateway', 'answer': 'We integrate payment systems like Stripe, PayPal, Square, and local payment providers with secure transaction handling.', 'category': 'integration', 'tags': ['payment', 'stripe', 'paypal']},

    # ==== AUTOMATION ====
    {'question': 'Automation', 'answer': 'We automate business processes including data entry, report generation, email workflows, and repetitive tasks to save time and reduce errors.', 'category': 'automation', 'tags': ['automation', 'workflow']},
    {'question': 'Workflow', 'answer': 'We create custom workflow automation systems that streamline your business processes from start to finish.', 'category': 'automation', 'tags': ['workflow', 'process']},
    {'question': 'Process automation', 'answer': 'We digitize and automate manual processes, connecting different systems and eliminating repetitive work.', 'category': 'automation', 'tags': ['process', 'automation']},
    {'question': 'RPA', 'answer': 'Robotic Process Automation (RPA) to handle repetitive digital tasks automatically, freeing up your team for strategic work.', 'category': 'automation', 'tags': ['rpa', 'robotics']},

    # ==== SECURITY ====
    {'question': 'Security', 'answer': 'We implement enterprise-grade security including encryption, secure authentication, HTTPS, regular security audits, and compliance with data protection regulations.', 'category': 'security', 'tags': ['security', 'safe']},
    {'question': 'Encryption', 'answer': 'We use industry-standard encryption for data at rest and in transit, protecting sensitive information.', 'category': 'security', 'tags': ['encryption', 'secure']},
    {'question': 'Authentication', 'answer': 'We implement secure authentication systems including OAuth, JWT, two-factor authentication, and single sign-on.', 'category': 'security', 'tags': ['auth', 'login', 'authentication']},
    {'question': 'GDPR', 'answer': 'We build GDPR-compliant systems with proper data handling, user consent management, and right to be forgotten features.', 'category': 'security', 'tags': ['gdpr', 'compliance']},
    {'question': 'SSL certificate', 'answer': 'All our websites include SSL certificates for HTTPS encryption, ensuring secure data transmission.', 'category': 'security', 'tags': ['ssl', 'https']},

    # ==== PROJECT & PRICING ====
    {'question': 'Timeline', 'answer': 'Project timelines depend on scope. Simple websites take 2-4 weeks, while complex applications can take 3-6 months. We provide detailed timelines after requirements analysis.', 'category': 'process', 'tags': ['timeline', 'duration']},
    {'question': 'Agile', 'answer': 'We follow Agile methodology with 2-week sprints, regular demos, and continuous feedback to ensure flexibility and quality.', 'category': 'process', 'tags': ['agile', 'methodology']},
    {'question': 'Project management', 'answer': 'We use tools like Jira, Trello, and Asana for transparent project management with regular updates and progress tracking.', 'category': 'process', 'tags': ['project management', 'tracking']},
    {'question': 'MVP', 'answer': 'We can build a Minimum Viable Product (MVP) to test your idea quickly, then iterate based on user feedback.', 'category': 'process', 'tags': ['mvp', 'prototype']},
    {'question': 'Prototype', 'answer': 'We create interactive prototypes and mockups to visualize your application before development begins.', 'category': 'process', 'tags': ['prototype', 'mockup']},

    # ==== SUPPORT & MAINTENANCE ====
    {'question': 'Support', 'answer': 'We offer ongoing support and maintenance including bug fixes, updates, monitoring, and technical assistance.', 'category': 'support', 'tags': ['support', 'help']},
    {'question': 'Maintenance', 'answer': 'Our maintenance plans include regular updates, security patches, performance optimization, and 24/7 monitoring.', 'category': 'support', 'tags': ['maintenance', 'updates']},
    {'question': 'Bug fix', 'answer': 'We provide rapid bug fixing with priority support, typically resolving critical issues within 24 hours.', 'category': 'support', 'tags': ['bug', 'fix', 'error']},
    {'question': 'Training', 'answer': 'We provide comprehensive training for your team on using and managing the software we develop.', 'category': 'support', 'tags': ['training', 'education']},
    {'question': 'Documentation', 'answer': 'We create detailed documentation including user guides, API docs, and technical specifications.', 'category': 'support', 'tags': ['documentation', 'docs']},

    # ==== INDUSTRIES ====
    {'question': 'Healthcare software', 'answer': 'We develop HIPAA-compliant healthcare applications including patient portals, appointment systems, and medical records management.', 'category': 'industry', 'tags': ['healthcare', 'medical']},
    {'question': 'Fintech', 'answer': 'We build secure financial technology solutions including payment systems, banking apps, and investment platforms.', 'category': 'industry', 'tags': ['fintech', 'finance', 'banking']},
    {'question': 'Education', 'answer': 'Learning management systems (LMS), online course platforms, and educational apps with student tracking and assessments.', 'category': 'industry', 'tags': ['education', 'learning', 'lms']},
    {'question': 'Real estate', 'answer': 'Property listing platforms, CRM systems for real estate agents, and virtual tour applications.', 'category': 'industry', 'tags': ['real estate', 'property']},
    {'question': 'Logistics', 'answer': 'Fleet management systems, shipment tracking, route optimization, and warehouse management solutions.', 'category': 'industry', 'tags': ['logistics', 'shipping', 'fleet']},

    # ==== TECHNOLOGIES ====
    {'question': 'Python', 'answer': 'We use Python for backend development, data processing, machine learning, and automation scripts.', 'category': 'tech', 'tags': ['python', 'programming']},
    {'question': 'JavaScript', 'answer': 'JavaScript for frontend interactivity, Node.js for backend, and React for modern user interfaces.', 'category': 'tech', 'tags': ['javascript', 'js']},
    {'question': 'Node.js', 'answer': 'Node.js for scalable server-side applications, real-time features, and microservices architecture.', 'category': 'tech', 'tags': ['nodejs', 'node']},
    {'question': 'TypeScript', 'answer': 'We use TypeScript for type-safe JavaScript development, reducing bugs and improving code quality.', 'category': 'tech', 'tags': ['typescript', 'ts']},
    {'question': 'Docker', 'answer': 'Docker containerization for consistent deployments across development, testing, and production environments.', 'category': 'tech', 'tags': ['docker', 'containers']},
    {'question': 'Kubernetes', 'answer': 'Kubernetes for container orchestration, auto-scaling, and managing complex microservices deployments.', 'category': 'tech', 'tags': ['kubernetes', 'k8s']},

    # ==== PERFORMANCE ====
    {'question': 'Performance', 'answer': 'We optimize applications for speed with caching, code optimization, CDN integration, and database indexing.', 'category': 'performance', 'tags': ['performance', 'speed']},
    {'question': 'Scalability', 'answer': 'We design systems to scale horizontally and vertically, handling growth from hundreds to millions of users.', 'category': 'performance', 'tags': ['scalability', 'scale']},
    {'question': 'Load balancing', 'answer': 'We implement load balancers to distribute traffic across multiple servers for reliability and performance.', 'category': 'performance', 'tags': ['load balancing', 'traffic']},
    {'question': 'Caching', 'answer': 'We use Redis, Memcached, and CDNs for caching to dramatically improve application speed.', 'category': 'performance', 'tags': ['caching', 'redis']},

    # ==== AI & MACHINE LEARNING ====
    {'question': 'AI', 'answer': 'We integrate artificial intelligence and machine learning for chatbots, recommendations, image recognition, and data analysis.', 'category': 'ai', 'tags': ['ai', 'artificial intelligence']},
    {'question': 'Machine learning', 'answer': 'We build ML models for predictive analytics, pattern recognition, and automated decision-making.', 'category': 'ai', 'tags': ['ml', 'machine learning']},
    {'question': 'Chatbot', 'answer': 'We develop AI-powered chatbots for customer support, lead generation, and automated assistance.', 'category': 'ai', 'tags': ['chatbot', 'bot']},
    {'question': 'Data analysis', 'answer': 'We provide data analytics solutions including dashboards, reporting, and business intelligence.', 'category': 'ai', 'tags': ['data', 'analytics', 'bi']},

    # ==== TESTING ====
    {'question': 'Testing', 'answer': 'We perform comprehensive testing including unit tests, integration tests, and end-to-end testing for quality assurance.', 'category': 'quality', 'tags': ['testing', 'qa']},
    {'question': 'Quality assurance', 'answer': 'Our QA process includes automated testing, manual testing, performance testing, and security testing.', 'category': 'quality', 'tags': ['qa', 'quality']},
    {'question': 'Code review', 'answer': 'We conduct thorough code reviews to maintain high code quality, security, and best practices.', 'category': 'quality', 'tags': ['code review', 'review']},

    # ==== MIGRATION & MODERNIZATION ====
    {'question': 'Legacy system', 'answer': 'We modernize legacy systems, migrating from outdated technology to modern platforms while preserving your data.', 'category': 'migration', 'tags': ['legacy', 'modernization']},
    {'question': 'Refactoring', 'answer': 'We refactor existing codebases to improve performance, maintainability, and add new features.', 'category': 'migration', 'tags': ['refactoring', 'improvement']},
    {'question': 'Technology upgrade', 'answer': 'We upgrade applications to latest versions of frameworks, libraries, and platforms with minimal disruption.', 'category': 'migration', 'tags': ['upgrade', 'modernize']},

    # ==== BUSINESS QUESTIONS ====
    {'question': 'Startup', 'answer': 'We work with startups from idea to launch, building MVPs quickly and iterating based on market feedback.', 'category': 'business', 'tags': ['startup', 'new business']},
    {'question': 'Enterprise', 'answer': 'We provide enterprise-grade solutions with high security, scalability, and integration with existing systems.', 'category': 'business', 'tags': ['enterprise', 'large company']},
    {'question': 'Small business', 'answer': 'We help small businesses with affordable solutions including websites, automation, and custom tools.', 'category': 'business', 'tags': ['small business', 'smb']},
    {'question': 'Contract', 'answer': 'We offer flexible contracts including fixed-price projects, time & materials, and dedicated team models.', 'category': 'business', 'tags': ['contract', 'agreement']},
    {'question': 'NDA', 'answer': 'We sign Non-Disclosure Agreements (NDA) to protect your confidential information and intellectual property.', 'category': 'business', 'tags': ['nda', 'confidentiality']},
    {'question': 'Intellectual property', 'answer': 'You retain all intellectual property rights to the software we develop for you.', 'category': 'business', 'tags': ['ip', 'ownership']},

    # ==== COMMUNICATION ====
    {'question': 'Communication', 'answer': 'We communicate via email, Slack, video calls, and project management tools with regular status updates.', 'category': 'process', 'tags': ['communication', 'contact']},
    {'question': 'Meeting', 'answer': 'We schedule regular meetings including sprint planning, demos, and status updates via Zoom or Google Meet.', 'category': 'process', 'tags': ['meeting', 'call']},
    {'question': 'Demo', 'answer': 'We provide regular demos of work in progress so you can see and test features as they\'re developed.', 'category': 'process', 'tags': ['demo', 'presentation']},
    {'question': 'Feedback', 'answer': 'We encourage continuous feedback throughout development to ensure the final product meets your expectations.', 'category': 'process', 'tags': ['feedback', 'input']},

    # ==== LOCATION & AVAILABILITY ====
    {'question': 'Remote work', 'answer': 'We work remotely with clients globally, using modern collaboration tools for seamless communication.', 'category': 'company', 'tags': ['remote', 'distributed']},
    {'question': 'Time zone', 'answer': 'We\'re based in South Africa (SAST) but we adjust our schedule to overlap with your business hours.', 'category': 'company', 'tags': ['timezone', 'hours']},
    {'question': 'On-site', 'answer': 'For local clients, we can provide on-site consultations and meetings as needed.', 'category': 'company', 'tags': ['onsite', 'visit']},

    # ==== PORTFOLIO & EXPERIENCE ====
    {'question': 'Portfolio', 'answer': 'We have experience across industries including healthcare, finance, education, e-commerce, and more. Contact us for case studies.', 'category': 'company', 'tags': ['portfolio', 'work']},
    {'question': 'Experience', 'answer': 'Our team has 10+ years of combined experience in software development, having delivered 200+ successful projects.', 'category': 'company', 'tags': ['experience', 'expertise']},
    {'question': 'References', 'answer': 'We can provide references from satisfied clients in various industries. Contact us for details.', 'category': 'company', 'tags': ['references', 'testimonials']},
    {'question': 'Case studies', 'answer': 'We have case studies showcasing our work across different industries and technologies. Contact us to learn more.', 'category': 'company', 'tags': ['case studies', 'examples']},

    # ==== SPECIFIC FEATURES ====
    {'question': 'User authentication', 'answer': 'We implement secure user authentication with features like login, signup, password reset, email verification, and role-based access.', 'category': 'features', 'tags': ['authentication', 'login']},
    {'question': 'Dashboard', 'answer': 'We create interactive dashboards with charts, graphs, and analytics for data visualization and business insights.', 'category': 'features', 'tags': ['dashboard', 'analytics']},
    {'question': 'Admin panel', 'answer': 'Custom admin panels for managing users, content, settings, and monitoring application performance.', 'category': 'features', 'tags': ['admin', 'backend']},
    {'question': 'Search functionality', 'answer': 'We implement powerful search with filters, auto-complete, and fuzzy matching using Elasticsearch or similar technologies.', 'category': 'features', 'tags': ['search', 'find']},
    {'question': 'Notifications', 'answer': 'Real-time notifications via email, SMS, push notifications, and in-app alerts for user engagement.', 'category': 'features', 'tags': ['notifications', 'alerts']},
    {'question': 'File upload', 'answer': 'Secure file upload and management with support for images, documents, videos with cloud storage integration.', 'category': 'features', 'tags': ['upload', 'files']},
    {'question': 'Real-time', 'answer': 'We build real-time features using WebSockets for chat, live updates, collaborative editing, and notifications.', 'category': 'features', 'tags': ['realtime', 'live']},
    {'question': 'Multi-language', 'answer': 'We implement internationalization (i18n) for multi-language support to reach global audiences.', 'category': 'features', 'tags': ['multilanguage', 'translation']},

    # ==== COMMON CONCERNS ====
    {'question': 'Warranty', 'answer': 'We provide a warranty period after delivery to fix any bugs or issues at no additional cost.', 'category': 'support', 'tags': ['warranty', 'guarantee']},
    {'question': 'Source code', 'answer': 'You receive complete source code and documentation for all software we develop for you.', 'category': 'business', 'tags': ['source code', 'code']},
    {'question': 'Updates after delivery', 'answer': 'We offer maintenance packages for ongoing updates, or you can manage updates with your own team using our documentation.', 'category': 'support', 'tags': ['updates', 'maintenance']},
    {'question': 'Changes during development', 'answer': 'We welcome changes during development through our Agile process, with clear communication about timeline and cost impacts.', 'category': 'process', 'tags': ['changes', 'modifications']},
    {'question': 'Project cancellation', 'answer': 'Our contracts include clear terms for project cancellation. You own all work completed up to that point.', 'category': 'business', 'tags': ['cancellation', 'termination']},

    # ==== GETTING STARTED ====
    {'question': 'Get started', 'answer': 'Contact us at info@eclick.co.za or call +27 76 740 1777 to schedule a free consultation and discuss your project.', 'category': 'getting started', 'tags': ['start', 'begin']},
    {'question': 'Consultation', 'answer': 'We offer free initial consultations to understand your needs and provide recommendations. No obligation required.', 'category': 'getting started', 'tags': ['consultation', 'meeting']},
    {'question': 'Proposal', 'answer': 'After discussing your requirements, we provide a detailed proposal with scope, timeline, and cost breakdown.', 'category': 'getting started', 'tags': ['proposal', 'quote']},
    {'question': 'Discovery phase', 'answer': 'We start with a discovery phase to understand requirements, define scope, and create a detailed project plan.', 'category': 'getting started', 'tags': ['discovery', 'requirements']},
    {'question': 'Requirements', 'answer': 'We help you define clear requirements through workshops, interviews, and documentation of your business needs.', 'category': 'getting started', 'tags': ['requirements', 'specifications']},
]

print(f"Adding {len(comprehensive_knowledge)} knowledge entries...")
print("This will significantly expand the AI's capabilities!\n")

for idx, item in enumerate(comprehensive_knowledge, 1):
    ai_service.add_knowledge(
        question=item['question'],
        answer=item['answer'],
        category=item['category'],
        tags=item['tags']
    )
    if idx % 20 == 0:
        print(f"  Progress: {idx}/{len(comprehensive_knowledge)} entries added...")

print(f"\n✓ Successfully added {len(comprehensive_knowledge)} knowledge entries!")

# Show final stats
stats = ai_service.get_learning_stats()
print(f"\nFinal AI Stats:")
print(f"  - Total Knowledge Base Size: {stats['knowledge_base_size']}")
print(f"  - Total Conversations: {stats['total_conversations']}")
print(f"\nThe chatbot can now answer questions about:")
print("  ✓ Web development & mobile apps")
print("  ✓ Cloud services & databases")
print("  ✓ APIs & integrations")
print("  ✓ Security & compliance")
print("  ✓ AI & machine learning")
print("  ✓ DevOps & automation")
print("  ✓ Industry-specific solutions")
print("  ✓ Project process & pricing")
print("  ✓ Support & maintenance")
print("  ✓ And much more!")
