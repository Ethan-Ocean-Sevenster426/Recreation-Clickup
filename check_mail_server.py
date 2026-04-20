"""
Check mail server configuration and reputation
"""

import socket
import subprocess

MAIL_SERVER = "mail.eclick.co.za"
MAIL_IP = "160.119.100.21"

print("="*70)
print("MAIL SERVER DIAGNOSTIC")
print("="*70)

# 1. Check reverse DNS
print(f"\n[1] REVERSE DNS (PTR) for {MAIL_IP}")
print("-"*50)
try:
    result = subprocess.run(['nslookup', MAIL_IP], capture_output=True, text=True, timeout=10)
    output = result.stdout

    if 'name =' in output.lower() or MAIL_SERVER in output:
        print(f"  [OK] Reverse DNS configured")
        for line in output.split('\n'):
            if 'name' in line.lower():
                print(f"      {line.strip()}")
    else:
        print(f"  [WARN] No reverse DNS found!")
        print(f"        This is CRITICAL for email delivery")
        print(f"        Add PTR record: {MAIL_IP} -> {MAIL_SERVER}")
except Exception as e:
    print(f"  [ERROR] {e}")

# 2. Check if IP is blacklisted
print(f"\n[2] BLACKLIST CHECK for {MAIL_IP}")
print("-"*50)

blacklists = [
    'zen.spamhaus.org',
    'bl.spamcop.net',
    'dnsbl.sorbs.net',
    'b.barracudacentral.org',
    'cbl.abuseat.org',
]

reversed_ip = '.'.join(reversed(MAIL_IP.split('.')))
found_on = []

for bl in blacklists:
    try:
        query = f"{reversed_ip}.{bl}"
        socket.gethostbyname(query)
        print(f"  [FAIL] BLACKLISTED on {bl}")
        found_on.append(bl)
    except socket.gaierror:
        print(f"  [OK] Not on {bl}")
    except Exception as e:
        print(f"  [?] Could not check {bl}")

# 3. Check DKIM
print(f"\n[3] DKIM CONFIGURATION")
print("-"*50)
try:
    result = subprocess.run(
        ['nslookup', '-type=TXT', f'default._domainkey.eclick.co.za'],
        capture_output=True, text=True, timeout=10
    )
    if 'v=DKIM1' in result.stdout:
        print(f"  [OK] DKIM record exists")
        print(f"      But check if mail server is SIGNING emails!")
    else:
        print(f"  [WARN] DKIM record not found")
except Exception as e:
    print(f"  [ERROR] {e}")

# 4. Check current SPF
print(f"\n[4] SPF RECORD CHECK")
print("-"*50)
try:
    result = subprocess.run(
        ['nslookup', '-type=TXT', 'eclick.co.za', 'ns1.datakeepers.co.za'],
        capture_output=True, text=True, timeout=10
    )

    if f'ip4:{MAIL_IP}' in result.stdout:
        print(f"  [OK] SPF includes {MAIL_IP}")
    else:
        print(f"  [WARN] SPF might not include mail server IP")
        print(f"        Current SPF:")
        for line in result.stdout.split('\n'):
            if 'v=spf1' in line:
                print(f"        {line.strip()}")
except Exception as e:
    print(f"  [ERROR] {e}")

# Summary
print(f"\n{'='*70}")
print("DIAGNOSIS")
print(f"{'='*70}")

if found_on:
    print(f"\n  CRITICAL: IP is BLACKLISTED on {len(found_on)} list(s)!")
    print(f"  You MUST request delisting:")
    for bl in found_on:
        print(f"    - {bl}")
else:
    print(f"\n  Most likely issues:")
    print(f"  1. REVERSE DNS (PTR) - Check if {MAIL_IP} -> {MAIL_SERVER}")
    print(f"  2. DKIM SIGNING - Mail server might not be signing outbound emails")
    print(f"  3. MAIL QUEUE - Emails might be stuck in queue")
    print(f"  4. PORT 25 - ISP might be blocking outbound SMTP")

print(f"\n  NEXT STEPS:")
print(f"  1. Contact your hosting provider (mail.eclick.co.za)")
print(f"  2. Ask them to check:")
print(f"     - Is reverse DNS (PTR) configured?")
print(f"     - Is DKIM signing enabled?")
print(f"     - Are emails leaving the server?")
print(f"     - Check mail queue and logs")
print(f"  3. Or switch to a reliable email service:")
print(f"     - SendGrid (100 emails/day free)")
print(f"     - Mailgun (5000 emails/month free)")
print(f"     - Amazon SES (very cheap)")

print(f"\n{'='*70}")
