"""
Comprehensive email diagnostic test.
"""

import os
import django
import socket
import smtplib
import ssl

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.conf import settings
from django.core.mail import get_connection

def run_email_diagnostics():
    """Run comprehensive email diagnostics"""
    
    print("=" * 60)
    print("EMAIL DIAGNOSTIC TEST")
    print("=" * 60)
    
    # 1. Check email settings
    print("\n[1] EMAIL CONFIGURATION")
    print("-" * 40)
    print(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"  EMAIL_HOST_PASSWORD: {'*' * 8 if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
    print(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"  EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
    print(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    # 2. DNS Resolution
    print("\n[2] DNS RESOLUTION")
    print("-" * 40)
    try:
        ip = socket.gethostbyname(settings.EMAIL_HOST)
        print(f"  [OK] {settings.EMAIL_HOST} resolves to {ip}")
    except socket.gaierror as e:
        print(f"  [FAIL] Cannot resolve {settings.EMAIL_HOST}: {e}")
        return False
    
    # 3. Port connectivity
    print("\n[3] PORT CONNECTIVITY")
    print("-" * 40)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((settings.EMAIL_HOST, settings.EMAIL_PORT))
        sock.close()
        
        if result == 0:
            print(f"  [OK] Port {settings.EMAIL_PORT} is open")
        else:
            print(f"  [FAIL] Port {settings.EMAIL_PORT} is closed or blocked")
            return False
    except Exception as e:
        print(f"  [FAIL] Connection error: {e}")
        return False
    
    # 4. SMTP Connection Test
    print("\n[4] SMTP CONNECTION TEST")
    print("-" * 40)
    try:
        if settings.EMAIL_USE_SSL:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, context=context, timeout=30)
        else:
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=30)
            
        server.set_debuglevel(0)
        
        # EHLO
        code, msg = server.ehlo()
        print(f"  [OK] EHLO response: {code}")
        
        # STARTTLS if using TLS
        if settings.EMAIL_USE_TLS and not settings.EMAIL_USE_SSL:
            code, msg = server.starttls()
            print(f"  [OK] STARTTLS: {code}")
            server.ehlo()
        
        # Login
        if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            print(f"  [OK] Authentication successful")
        else:
            print(f"  [WARN] No authentication credentials")
        
        server.quit()
        print(f"  [OK] SMTP connection test passed")
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"  [FAIL] Authentication failed: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"  [FAIL] SMTP error: {e}")
        return False
    except Exception as e:
        print(f"  [FAIL] Connection error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. Django connection test
    print("\n[5] DJANGO EMAIL CONNECTION")
    print("-" * 40)
    try:
        connection = get_connection()
        connection.open()
        print(f"  [OK] Django email connection opened")
        connection.close()
    except Exception as e:
        print(f"  [FAIL] Django connection error: {e}")
        return False
    
    # 6. Send actual test email with verbose output
    print("\n[6] SENDING TEST EMAIL")
    print("-" * 40)
    
    from django.core.mail import EmailMessage
    
    try:
        email = EmailMessage(
            subject='E-Click Diagnostic Test',
            body='This is a diagnostic test email from E-Click.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['chris.delport@eclick.co.za'],
            headers={'X-Test': 'Diagnostic'}
        )
        
        result = email.send(fail_silently=False)
        
        if result:
            print(f"  [OK] Email sent successfully")
            print(f"  [OK] Result: {result} email(s) queued")
        else:
            print(f"  [FAIL] Send returned 0")
            
    except Exception as e:
        print(f"  [FAIL] Send error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 7. Common issues check
    print("\n[7] COMMON ISSUES CHECK")
    print("-" * 40)
    
    issues = []
    
    # Check if from email matches authenticated user
    if settings.EMAIL_HOST_USER != settings.DEFAULT_FROM_EMAIL:
        if settings.EMAIL_HOST_USER.split('@')[1] != settings.DEFAULT_FROM_EMAIL.split('@')[1]:
            issues.append("From email domain doesn't match authenticated domain")
    
    # Check for missing password
    if not settings.EMAIL_HOST_PASSWORD:
        issues.append("EMAIL_HOST_PASSWORD is not set")
    
    # Check port
    if settings.EMAIL_PORT == 25:
        issues.append("Port 25 is often blocked by ISPs")
    
    if issues:
        for issue in issues:
            print(f"  [WARN] {issue}")
    else:
        print(f"  [OK] No obvious issues found")
    
    # 8. Recommendations
    print("\n[8] RECOMMENDATIONS")
    print("-" * 40)
    print("  If emails still not received:")
    print("  1. Check spam/junk folder")
    print("  2. Verify SPF record for eclick.co.za")
    print("  3. Check DKIM is configured")
    print("  4. Review mail server logs")
    print("  5. Test with external email (gmail, etc)")
    
    return True

if __name__ == "__main__":
    success = run_email_diagnostics()
    
    print("\n" + "=" * 60)
    if success:
        print("DIAGNOSTIC COMPLETE - All tests passed")
        print("Email system appears to be working correctly.")
        print("Issue may be with recipient's mail server or spam filters.")
    else:
        print("DIAGNOSTIC FAILED - Check errors above")
    print("=" * 60)
