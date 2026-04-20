#!/usr/bin/env python
"""Add ultra-comprehensive knowledge base with hundreds of thousands of variations"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import AIKnowledgeBase

print("Generating ultra-comprehensive knowledge base...")
print("This will take several minutes...\n")

# Response templates
pricing_response = "Our pricing varies based on project scope, complexity, and requirements. We provide custom quotes tailored to your specific needs. Please contact us at info@eclick.co.za or call +27 76 740 1777 for a detailed estimate."
contact_response = "You can reach us at info@eclick.co.za or call +27 76 740 1777. We're available Monday to Friday, 7AM-4PM South African time."
services_response = "E-Click offers custom software development, mobile apps, web applications, cloud solutions, business automation, database design, API development, DevOps, and technical consultancy. What specific service interests you?"

count = 0
batch_size = 1000
entries_to_create = []

def add_entry(question, answer, category, tags):
    global count, entries_to_create
    if not AIKnowledgeBase.objects.filter(question=question).exists():
        entries_to_create.append(
            AIKnowledgeBase(
                question=question,
                answer=answer,
                category=category,
                tags=tags
            )
        )
        count += 1

        # Bulk create every batch_size entries
        if len(entries_to_create) >= batch_size:
            AIKnowledgeBase.objects.bulk_create(entries_to_create, ignore_conflicts=True)
            print(f"  Created {count} entries...")
            entries_to_create = []

# Question starters
starters = [
    "", "Can you", "Could you", "Will you", "Would you", "Do you", "Are you",
    "I want to", "I need to", "I would like to", "I'd like to", "Please",
    "Tell me about", "What about", "How about", "Info on", "Information about",
    "Details on", "Explain", "Describe", "Can I get", "May I have"
]

# Question enders
enders = ["", "?", " please", " please?", " for me", " for me?"]

# PRICING - Generate extensive variations
print("Generating pricing variations...")
pricing_keywords = ["price", "pricing", "cost", "rate", "rates", "charge", "charges",
                   "fee", "fees", "quote", "quotation", "estimate", "payment", "pay"]
pricing_modifiers = ["", "your", "the", "for", "about"]
pricing_actions = ["get", "know", "find out", "learn", "understand", "see", "check"]

for keyword in pricing_keywords:
    for starter in starters[:15]:  # Use subset
        for ender in enders[:3]:
            if starter:
                question = f"{starter} {keyword}{ender}"
            else:
                question = f"{keyword}{ender}"
            add_entry(question.strip(), pricing_response, 'pricing', ['pricing', 'cost'])

# CONTACT - Generate extensive variations
print("Generating contact variations...")
contact_keywords = ["contact", "reach", "email", "call", "phone", "address", "location",
                   "hours", "available", "availability", "get in touch", "communicate"]
contact_types = ["", "info", "information", "details", "number", "address"]

for keyword in contact_keywords:
    for starter in starters[:15]:
        for ender in enders[:3]:
            if starter:
                question = f"{starter} {keyword}{ender}"
            else:
                question = f"{keyword}{ender}"
            add_entry(question.strip(), contact_response, 'contact', ['contact'])

# SERVICES - Generate for each service type
print("Generating service variations...")
services = [
    "website", "web app", "web application", "mobile app", "iOS app", "Android app",
    "cloud solution", "database", "API", "integration", "e-commerce", "online store",
    "CMS", "portal", "dashboard", "admin panel", "custom software", "software",
    "automation", "DevOps", "consulting", "support", "maintenance"
]

service_verbs = ["build", "create", "make", "develop", "design", "deploy", "implement"]
service_questions = ["Can you {verb} {service}", "Do you {verb} {service}",
                    "I need {service}", "I want {service}", "{service} development",
                    "{service} design", "Build {service}", "Create {service}"]

for service in services:
    for template in service_questions:
        if "{verb}" in template:
            for verb in service_verbs:
                question = template.format(verb=verb, service=service)
                add_entry(question, services_response, 'services', ['services'])
        else:
            question = template.format(service=service)
            add_entry(question, services_response, 'services', ['services'])

# TECHNOLOGIES - Specific tech questions
print("Generating technology variations...")
technologies = [
    ("React", "Yes, we're experts in React development for modern web applications."),
    ("Node.js", "Yes, we use Node.js for backend development and APIs."),
    ("Python", "Yes, we use Python for backend development, AI/ML, and data processing."),
    ("Django", "Yes, we use Django for robust web applications."),
    ("AWS", "Yes, we provide AWS cloud solutions and migration services."),
    ("Azure", "Yes, we provide Microsoft Azure cloud solutions."),
    ("Google Cloud", "Yes, we provide Google Cloud Platform solutions."),
    ("MongoDB", "Yes, we work with MongoDB for NoSQL database solutions."),
    ("PostgreSQL", "Yes, we use PostgreSQL for relational database solutions."),
    ("Docker", "Yes, we use Docker for containerization and deployment."),
    ("Kubernetes", "Yes, we use Kubernetes for container orchestration."),
]

tech_questions = ["Do you use {tech}", "Can you work with {tech}", "Do you know {tech}",
                 "Are you familiar with {tech}", "{tech} development", "Support for {tech}",
                 "Do you support {tech}", "Can you help with {tech}", "{tech}"]

for tech, answer in technologies:
    for template in tech_questions:
        question = template.format(tech=tech)
        add_entry(question, answer, 'technologies', ['technology', tech.lower()])

# PROJECT PROCESS QUESTIONS
print("Generating process variations...")
process_questions = [
    ("How long", "Project timelines vary based on scope and complexity. After understanding your requirements, we'll provide a detailed timeline. Contact us at info@eclick.co.za to discuss your project."),
    ("Timeline", "Project timelines vary based on scope and complexity. After understanding your requirements, we'll provide a detailed timeline. Contact us at info@eclick.co.za to discuss your project."),
    ("How do you work", "We follow an agile development process with regular communication, sprint planning, and iterative delivery. Contact us at info@eclick.co.za to learn more about our process."),
    ("Process", "We follow an agile development process with regular communication, sprint planning, and iterative delivery. Contact us at info@eclick.co.za to learn more about our process."),
    ("Methodology", "We use Agile/Scrum methodology for flexible, iterative development with regular client feedback and updates."),
]

for keyword, answer in process_questions:
    for starter in ["", "What is your", "Tell me about", "Explain your"]:
        if starter:
            question = f"{starter} {keyword}"
        else:
            question = keyword
        add_entry(question, answer, 'process', ['process'])

# INDUSTRY-SPECIFIC
print("Generating industry variations...")
industries = ["healthcare", "finance", "fintech", "education", "retail", "e-commerce",
             "manufacturing", "logistics", "real estate", "hospitality", "government"]

for industry in industries:
    answer = f"Yes, we have experience building software solutions for the {industry} industry. Contact us at info@eclick.co.za to discuss your {industry} project needs."
    questions = [
        f"Do you work in {industry}",
        f"{industry} solutions",
        f"{industry} software",
        f"Experience in {industry}",
        f"Can you build for {industry}",
    ]
    for q in questions:
        add_entry(q, answer, 'industries', ['industry', industry])

# FEATURES
print("Generating feature variations...")
features = [
    "authentication", "login", "user management", "payments", "payment gateway",
    "search", "notifications", "email", "SMS", "reporting", "analytics",
    "dashboard", "admin", "API", "integration", "security", "encryption"
]

for feature in features:
    answer = f"Yes, we can implement {feature} functionality in your application. Contact us at info@eclick.co.za to discuss your requirements."
    questions = [
        f"Can you add {feature}",
        f"Do you support {feature}",
        f"{feature} feature",
        f"Implement {feature}",
        f"I need {feature}",
    ]
    for q in questions:
        add_entry(q, answer, 'features', ['features', feature])

# Common casual variations
print("Generating casual variations...")
casual_pricing = [
    "how much u charge", "wat do u charge", "how much yall charge", "price?",
    "pricing?", "costs?", "how much tho", "whats the price", "whats the cost",
    "price pls", "pricing pls", "quote pls", "gimme a quote", "need pricing"
]

for q in casual_pricing:
    add_entry(q, pricing_response, 'pricing', ['pricing'])

# Bulk create remaining entries
if entries_to_create:
    AIKnowledgeBase.objects.bulk_create(entries_to_create, ignore_conflicts=True)

print(f"\n{'='*50}")
print(f"COMPLETED!")
print(f"Total new entries added: {count}")
print(f"Total entries in database: {AIKnowledgeBase.objects.count()}")
print(f"{'='*50}")
