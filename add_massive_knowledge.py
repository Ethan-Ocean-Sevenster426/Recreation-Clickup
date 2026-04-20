#!/usr/bin/env python
"""Add massive comprehensive knowledge base covering all scenarios"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import AIKnowledgeBase

# Standard responses
pricing_response = "Our pricing varies based on project scope, complexity, and requirements. We provide custom quotes tailored to your specific needs. Please contact us at info@eclick.co.za or call +27 76 740 1777 for a detailed estimate."
contact_response = "You can reach us at info@eclick.co.za or call +27 76 740 1777. We're available Monday to Friday, 7AM-4PM South African time."
services_response = "E-Click offers custom software development, mobile apps, web applications, cloud solutions, business automation, database design, API development, DevOps, and technical consultancy. What specific service interests you?"

# Pricing variations (comprehensive)
pricing_variations = [
    "How much", "What's the cost", "What does it cost", "Price", "Prices", "Pricing",
    "How much do you charge", "What are your prices", "What are your rates", "Rates",
    "Cost estimate", "Price estimate", "Quote", "Quotation", "Get a quote",
    "I need pricing", "I need a quote", "I want pricing information", "Pricing info",
    "Tell me the cost", "Tell me the price", "Tell me your rates", "Tell me pricing",
    "Can I get a quote", "Can you give me a price", "Can you quote me",
    "What do you charge", "What would it cost", "What's your pricing",
    "How expensive", "Is it expensive", "Affordable", "Budget", "Cost breakdown",
    "Pricing structure", "Price list", "Rate card", "Fee structure", "Fees",
    "Payment", "How much to pay", "What to pay", "Cost details", "Pricing details",
    "I want to know the cost", "I want to know the price", "I want to know pricing",
    "Tell me about pricing", "Tell me about cost", "Tell me about rates",
    "Pricing information", "Cost information", "Rate information",
    "How much does it cost", "How much will it cost", "How much would it cost",
    "What will it cost", "What would it cost", "What does your service cost",
    "Service pricing", "Service cost", "Service rates", "Project cost", "Project pricing",
    "Development cost", "Development pricing", "Software cost", "Software pricing",
    "App cost", "App pricing", "Website cost", "Website pricing",
    "How much for a website", "How much for an app", "How much for software",
    "Price for website", "Price for app", "Price for development",
    "Cost of website", "Cost of app", "Cost of software development",
    "Estimate cost", "Estimate price", "Give me an estimate", "Provide estimate",
    "I need cost estimate", "I need price estimate", "Cost estimation",
    "Ballpark figure", "Rough estimate", "Approximate cost", "Approximate price",
    "Your charges", "Charge", "Charging", "How do you charge",
    "Per hour", "Hourly rate", "Daily rate", "Monthly rate", "Fixed price",
    "Package pricing", "Packages", "Plans", "Pricing plans", "Service packages",
]

# Contact variations (comprehensive)
contact_variations = [
    "Contact", "Contact you", "Contact info", "Contact information", "Contact details",
    "How to contact", "How can I contact", "How do I contact", "Get in touch",
    "Reach you", "Reach out", "How to reach", "How can I reach you",
    "Email", "Email address", "Your email", "Contact email", "Email you",
    "What's your email", "Send email", "Email contact",
    "Phone", "Phone number", "Call", "Call you", "Telephone", "Tel",
    "What's your phone", "Contact number", "Phone contact", "Call number",
    "How to call", "Can I call", "Call details",
    "Address", "Location", "Where are you", "Your location", "Office location",
    "Physical address", "Office address", "Your address", "Where located",
    "Business hours", "Hours", "Working hours", "Office hours", "Open hours",
    "When are you open", "When open", "What time open", "Opening hours",
    "Available", "Availability", "When available", "Are you available",
    "Talk to someone", "Speak to someone", "Chat", "Discuss", "Consultation",
    "Meet", "Meeting", "Schedule meeting", "Book meeting", "Appointment",
    "Get help", "Need help", "Support", "Customer support", "Help desk",
    "Communicate", "Communication", "How to communicate",
]

# Services variations (extensive)
service_variations = [
    # General
    "Services", "What do you do", "What services", "Your services", "Service offerings",
    "What you offer", "Offerings", "What can you do", "Capabilities",
    "What do you provide", "What you provide", "Solutions", "Your solutions",

    # Web development
    "Website", "Web development", "Build website", "Create website", "Make website",
    "Web app", "Web application", "Web design", "Website design",
    "Responsive website", "Mobile website", "E-commerce", "Online store",
    "Shopping cart", "CMS", "Content management", "WordPress", "Drupal",

    # Mobile development
    "Mobile app", "App development", "iOS app", "Android app", "Mobile application",
    "Build app", "Create app", "Make app", "Native app", "Cross-platform app",
    "React Native", "Flutter", "Ionic", "Hybrid app",

    # Cloud
    "Cloud", "Cloud solutions", "Cloud services", "AWS", "Azure", "Google Cloud",
    "Cloud hosting", "Cloud infrastructure", "Cloud migration", "Cloud deployment",
    "Serverless", "Lambda", "Cloud storage", "Cloud computing",

    # Database
    "Database", "Database design", "SQL", "NoSQL", "MongoDB", "PostgreSQL",
    "MySQL", "Database development", "Data modeling", "Database optimization",

    # API
    "API", "API development", "REST API", "GraphQL", "API integration",
    "Third-party integration", "Integration services", "Webhook",

    # Other services
    "DevOps", "CI/CD", "Automation", "Testing", "QA", "Quality assurance",
    "Maintenance", "Support", "Bug fixes", "Updates", "Upgrades",
    "Consulting", "Technical consulting", "Architecture", "System design",
]

# Common questions
common_questions = [
    ("Who are you", "I'm the E-Click AI assistant! I'm here to help answer your questions about our software development services, pricing, contact details, and more."),
    ("What is E-Click", "E-Click is a software development company specializing in custom software solutions, mobile apps, web applications, cloud infrastructure, and business automation. We help businesses grow through innovative technology."),
    ("About E-Click", "E-Click is a software development company specializing in custom software solutions, mobile apps, web applications, cloud infrastructure, and business automation. We help businesses grow through innovative technology."),
    ("Company info", "E-Click is a software development company specializing in custom software solutions, mobile apps, web applications, cloud infrastructure, and business automation. We help businesses grow through innovative technology."),
    ("Years of experience", "E-Click has over 10 years of experience delivering innovative software solutions since 2014."),
    ("Experience", "E-Click has over 10 years of experience delivering innovative software solutions since 2014."),
    ("Portfolio", "We've completed over 200 successful projects across various industries. Contact us at info@eclick.co.za to see relevant case studies for your industry."),
    ("Case studies", "We've completed over 200 successful projects across various industries. Contact us at info@eclick.co.za to see relevant case studies for your industry."),
    ("Clients", "We work with 50+ enterprise clients including Fortune 500 companies. Our clients include FSA, NAB, Prokon, and SAMIC."),
    ("Technologies", "We work with React, Node.js, Python, Django, Kubernetes, AWS, Azure, Google Cloud, PostgreSQL, MongoDB, and many other modern technologies."),
    ("Tech stack", "We work with React, Node.js, Python, Django, Kubernetes, AWS, Azure, Google Cloud, PostgreSQL, MongoDB, and many other modern technologies."),
]

print("Adding massive comprehensive knowledge base...")
print("This will take a few minutes...\n")

count = 0

# Add pricing variations
print("Adding pricing variations...")
for question in pricing_variations:
    if not AIKnowledgeBase.objects.filter(question=question).exists():
        AIKnowledgeBase.objects.create(
            question=question,
            answer=pricing_response,
            category='pricing',
            tags=['pricing', 'cost', 'quote']
        )
        count += 1

print(f"Added {count} pricing entries")

# Add contact variations
temp = count
print("Adding contact variations...")
for question in contact_variations:
    if not AIKnowledgeBase.objects.filter(question=question).exists():
        AIKnowledgeBase.objects.create(
            question=question,
            answer=contact_response,
            category='contact',
            tags=['contact', 'info']
        )
        count += 1

print(f"Added {count - temp} contact entries")

# Add service variations
temp = count
print("Adding service variations...")
for question in service_variations:
    if not AIKnowledgeBase.objects.filter(question=question).exists():
        AIKnowledgeBase.objects.create(
            question=question,
            answer=services_response,
            category='services',
            tags=['services', 'offerings']
        )
        count += 1

print(f"Added {count - temp} service entries")

# Add common questions
temp = count
print("Adding common questions...")
for question, answer in common_questions:
    if not AIKnowledgeBase.objects.filter(question=question).exists():
        AIKnowledgeBase.objects.create(
            question=question,
            answer=answer,
            category='general',
            tags=['general', 'info']
        )
        count += 1

print(f"Added {count - temp} common question entries")

print(f"\nTotal new entries added: {count}")
print(f"Total entries in database: {AIKnowledgeBase.objects.count()}")
print("\nDone!")
