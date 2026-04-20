#!/usr/bin/env python3
"""
Script to fix hardcoded email addresses in email service
"""

import re

def fix_email_sender():
    """Replace hardcoded email addresses with None to use OAuth2 account"""
    
    # Read the email service file
    with open('home/email_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all instances of hardcoded email addresses
    # This will make the service use the OAuth2 account email instead
    content = re.sub(
        r"from_email='reports@eclick\.com'",
        "from_email=None,  # Will use OAuth2 account email",
        content
    )
    
    # Also fix the services.py file
    with open('home/services.py', 'r', encoding='utf-8') as f:
        services_content = f.read()
    
    services_content = re.sub(
        r"from_email='reports@eclick\.com'",
        "from_email=None,  # Will use OAuth2 account email",
        services_content
    )
    
    # Write the updated content back
    with open('home/email_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    with open('home/services.py', 'w', encoding='utf-8') as f:
        f.write(services_content)
    
    print("✅ Fixed hardcoded email addresses in email service files")
    print("📧 Emails will now be sent from the OAuth2 account (mocptydata@gmail.com)")

if __name__ == "__main__":
    fix_email_sender()
