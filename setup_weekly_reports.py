#!/usr/bin/env python3
"""
Setup script for weekly client reports system

This script helps you set up automated weekly client reports.
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings

def main():
    print("🚀 E-Click Weekly Client Reports Setup")
    print("=" * 50)
    
    # Check if email settings are configured
    print("\n📧 Checking email configuration...")
    
    if not hasattr(settings, 'EMAIL_HOST') or not settings.EMAIL_HOST:
        print("❌ EMAIL_HOST not configured in settings.py")
        print("   Please configure your email settings first.")
        return False
    
    if not hasattr(settings, 'EMAIL_HOST_USER') or not settings.EMAIL_HOST_USER:
        print("❌ EMAIL_HOST_USER not configured in settings.py")
        print("   Please configure your email settings first.")
        return False
    
    print("✅ Email settings are configured")
    
    # Test the weekly reports command with dry-run
    print("\n🧪 Testing weekly reports command (dry-run)...")
    try:
        call_command('send_weekly_reports', '--dry-run')
        print("✅ Weekly reports command is working correctly")
    except Exception as e:
        print(f"❌ Error testing weekly reports command: {e}")
        return False
    
    # Show setup instructions
    print("\n📋 Setup Instructions:")
    print("=" * 50)
    
    print("\n1. **Manual Testing (Optional):**")
    print("   Test sending a report to a specific client:")
    print("   python manage.py send_weekly_reports --client <username>")
    
    print("\n2. **Automated Weekly Reports:**")
    print("   Set up a cron job to run every Monday at 9:00 AM:")
    print("   # Add this line to your crontab (crontab -e):")
    print("   0 9 * * 1 cd /path/to/your/project && python manage.py send_weekly_reports")
    
    print("\n3. **Alternative: Systemd Timer (Linux):**")
    print("   Create a systemd service and timer for more control:")
    print("   See: https://wiki.archlinux.org/title/Systemd/Timers")
    
    print("\n4. **Windows Task Scheduler:**")
    print("   Create a scheduled task to run weekly:")
    print("   python manage.py send_weekly_reports")
    
    print("\n5. **Cloud Services:**")
    print("   - GitHub Actions (free tier available)")
    print("   - AWS Lambda with EventBridge")
    print("   - Google Cloud Functions with Cloud Scheduler")
    
    print("\n6. **Monitoring:**")
    print("   Check logs for any errors:")
    print("   tail -f /var/log/your-app.log")
    
    print("\n7. **Customization:**")
    print("   Edit home/management/commands/send_weekly_reports.py")
    print("   to modify report content or frequency")
    
    # Check if there are active clients
    from home.models import Client
    active_clients = Client.objects.filter(is_active=True).count()
    
    print(f"\n📊 Current Status:")
    print(f"   Active clients: {active_clients}")
    
    if active_clients == 0:
        print("   ⚠️  No active clients found. Reports won't be sent.")
        print("   Create some clients first to test the system.")
    
    print("\n✅ Setup complete! Your weekly client reports system is ready.")
    print("\n💡 Pro Tips:")
    print("   - Test with --dry-run first to see what would be sent")
    print("   - Monitor your email logs for delivery issues")
    print("   - Consider timezone differences when scheduling")
    print("   - Backup your cron/systemd configurations")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
