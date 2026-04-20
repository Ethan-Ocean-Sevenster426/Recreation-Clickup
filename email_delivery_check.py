"""
Email Delivery Diagnostic - Checks WHY emails aren't being received.
Tests DNS records (SPF/DKIM/DMARC) and mail server reputation.
"""

import os
import django
import socket
import subprocess

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.conf import settings
from django.core.mail import EmailMessage

def check_dns_records(domain):
    """Check SPF, DKIM, and DMARC records for a domain"""
    print(f"\n[DNS RECORDS] Checking {domain}")
    print("-" * 50)

    records = {}

    # Check SPF record
    try:
        result = subprocess.run(
            ['nslookup', '-type=TXT', domain],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout

        if 'v=spf1' in output:
            # Extract SPF record
            for line in output.split('\n'):
                if 'v=spf1' in line:
                    print(f"  [OK] SPF Record Found:")
                    print(f"       {line.strip()}")
                    records['spf'] = True
                    break
        else:
            print(f"  [WARN] No SPF record found!")
            print(f"         Add: v=spf1 include:mail.{domain} ~all")
            records['spf'] = False
    except Exception as e:
        print(f"  [ERROR] Could not check SPF: {e}")
        records['spf'] = None

    # Check DMARC record
    try:
        result = subprocess.run(
            ['nslookup', '-type=TXT', f'_dmarc.{domain}'],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout

        if 'v=DMARC1' in output:
            for line in output.split('\n'):
                if 'v=DMARC1' in line:
                    print(f"  [OK] DMARC Record Found:")
                    print(f"       {line.strip()}")
                    records['dmarc'] = True
                    break
        else:
            print(f"  [WARN] No DMARC record found!")
            print(f"         Add: v=DMARC1; p=none; rua=mailto:admin@{domain}")
            records['dmarc'] = False
    except Exception as e:
        print(f"  [ERROR] Could not check DMARC: {e}")
        records['dmarc'] = None

    # Check MX records
    try:
        result = subprocess.run(
            ['nslookup', '-type=MX', domain],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout

        if 'mail exchanger' in output.lower() or 'mx' in output.lower():
            print(f"  [OK] MX Records Found")
            records['mx'] = True
        else:
            print(f"  [WARN] No MX records found!")
            records['mx'] = False
    except Exception as e:
        print(f"  [ERROR] Could not check MX: {e}")
        records['mx'] = None

    return records

def check_blacklists(ip):
    """Check if IP is on common blacklists"""
    print(f"\n[BLACKLIST CHECK] Checking {ip}")
    print("-" * 50)

    # Common DNSBL servers
    blacklists = [
        'zen.spamhaus.org',
        'bl.spamcop.net',
        'dnsbl.sorbs.net',
        'b.barracudacentral.org',
    ]

    # Reverse the IP for DNSBL lookup
    reversed_ip = '.'.join(reversed(ip.split('.')))

    found_on = []
    for bl in blacklists:
        try:
            query = f"{reversed_ip}.{bl}"
            socket.gethostbyname(query)
            print(f"  [FAIL] Listed on {bl}")
            found_on.append(bl)
        except socket.gaierror:
            print(f"  [OK] Not on {bl}")
        except Exception as e:
            print(f"  [?] Could not check {bl}: {e}")

    return found_on

def send_test_with_headers(to_email, test_name):
    """Send test email with diagnostic headers"""
    print(f"\n  Sending to: {to_email}")

    try:
        subject = f'E-Click Delivery Test - {test_name}'
        body = f"""This is a delivery test email from E-Click.

Test: {test_name}
To: {to_email}
From: {settings.DEFAULT_FROM_EMAIL}

IMPORTANT: If you receive this email, please check:
1. Did it land in INBOX or SPAM/JUNK?
2. Check the email headers for SPF/DKIM/DMARC results

Steps to check headers:
- Gmail: Click 3 dots > "Show original"
- Outlook: Click 3 dots > "View message source"

Look for:
- spf=pass or spf=fail
- dkim=pass or dkim=fail
- dmarc=pass or dmarc=fail

If you see "fail" on any of these, that's why emails aren't being delivered.

Best regards,
E-Click Team
"""

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
            headers={
                'X-Mailer': 'E-Click Diagnostic',
                'X-Priority': '1',  # High priority
                'Importance': 'High',
                'X-Test-Name': test_name,
            }
        )

        result = email.send(fail_silently=False)

        if result:
            print(f"  [SENT] Email accepted by server")
            return True
        else:
            print(f"  [FAIL] Server rejected email")
            return False

    except Exception as e:
        print(f"  [ERROR] {type(e).__name__}: {e}")
        return False

def run_delivery_diagnostic():
    """Run comprehensive delivery diagnostic"""

    print("=" * 70)
    print("EMAIL DELIVERY DIAGNOSTIC")
    print("=" * 70)
    print("\nThis test checks WHY emails aren't being received,")
    print("even though they're being sent successfully.")

    # Get mail server IP
    try:
        mail_ip = socket.gethostbyname(settings.EMAIL_HOST)
        print(f"\nMail Server: {settings.EMAIL_HOST} ({mail_ip})")
    except:
        mail_ip = None
        print(f"\nMail Server: {settings.EMAIL_HOST} (IP lookup failed)")

    # Check DNS records
    domain = settings.EMAIL_HOST_USER.split('@')[1]
    dns_records = check_dns_records(domain)

    # Check blacklists
    if mail_ip:
        blacklists = check_blacklists(mail_ip)
    else:
        blacklists = []

    # Send test emails to multiple providers
    print("\n" + "=" * 70)
    print("[TEST EMAILS] Sending to multiple providers")
    print("=" * 70)

    test_emails = [
        ('ethan.sevenster@moc-pty.com', 'External Domain'),
    ]

    # Add more test emails if you have them
    # test_emails.append(('test@gmail.com', 'Gmail'))
    # test_emails.append(('test@outlook.com', 'Outlook'))

    results = []
    for email, name in test_emails:
        success = send_test_with_headers(email, name)
        results.append((email, name, success))

    # Summary and recommendations
    print("\n" + "=" * 70)
    print("DIAGNOSIS & RECOMMENDATIONS")
    print("=" * 70)

    issues = []

    if not dns_records.get('spf'):
        issues.append("Missing SPF record")
    if not dns_records.get('dmarc'):
        issues.append("Missing DMARC record")
    if blacklists:
        issues.append(f"IP blacklisted on: {', '.join(blacklists)}")

    if issues:
        print("\n  ISSUES FOUND:")
        for issue in issues:
            print(f"    - {issue}")

        print("\n  SOLUTIONS:")

        if not dns_records.get('spf'):
            print("""
    1. ADD SPF RECORD to your DNS:
       Type: TXT
       Host: @
       Value: v=spf1 ip4:{mail_ip} include:mail.eclick.co.za ~all

       Or if using cPanel: v=spf1 +a +mx +ip4:{mail_ip} ~all
""".format(mail_ip=mail_ip or 'YOUR_SERVER_IP'))

        if not dns_records.get('dmarc'):
            print("""
    2. ADD DMARC RECORD to your DNS:
       Type: TXT
       Host: _dmarc
       Value: v=DMARC1; p=none; rua=mailto:admin@eclick.co.za
""")

        if blacklists:
            print("""
    3. REMOVE FROM BLACKLISTS:
       - Visit each blacklist's website
       - Request delisting
       - This may take 24-48 hours
""")

        print("""
    4. ENABLE DKIM (in cPanel or mail server):
       - Go to cPanel > Email Deliverability
       - Enable DKIM for eclick.co.za
       - This adds cryptographic signatures to emails
""")

    else:
        print("""
  DNS RECORDS LOOK GOOD!

  If emails still aren't being received, the issue may be:

  1. RECIPIENT'S SPAM FILTER
     - Ask recipient to check spam/junk folder
     - Ask them to whitelist sender@eclick.co.za

  2. DKIM NOT ENABLED
     - Check cPanel > Email Deliverability
     - Enable DKIM signing

  3. CONTENT FILTERING
     - Avoid spam trigger words in subject/body
     - Don't use excessive links or images

  4. MAIL SERVER REPUTATION
     - The server may have low reputation
     - Consider using a dedicated email service:
       * SendGrid (free tier: 100 emails/day)
       * Mailgun (free tier: 5,000 emails/month)
       * Amazon SES (very cheap)
""")

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("""
  1. Check if test emails arrived (may be in spam)

  2. If in spam, check email headers for:
     - spf=fail (need SPF record)
     - dkim=fail (need DKIM enabled)
     - dmarc=fail (need DMARC record)

  3. Add missing DNS records (see above)

  4. If still failing, consider SendGrid/Mailgun

  5. Test again after DNS changes (wait 1-24 hours)
""")

    return dns_records, blacklists, results

if __name__ == "__main__":
    run_delivery_diagnostic()
