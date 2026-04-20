"""
One-time script to sync all project emails with their corresponding client emails
This fixes the current data inconsistency
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick_project.settings')
django.setup()

from home.models import Project, Client

def sync_all_emails():
    """Sync all project emails with their client model emails"""

    print(f"\n{'='*60}")
    print("SYNCING PROJECT EMAILS WITH CLIENT MODEL")
    print(f"{'='*60}\n")

    projects = Project.objects.all()
    updated_count = 0
    skipped_count = 0
    error_count = 0

    for project in projects:
        if project.client_username:
            try:
                client = Client.objects.get(username=project.client_username)

                # Check if sync is needed
                if project.client_email != client.email:
                    old_email = project.client_email
                    project.client_email = client.email
                    project.save()

                    print(f"[UPDATED] Project: {project.name}")
                    print(f"  Old email: {old_email}")
                    print(f"  New email: {client.email}")
                    print()

                    updated_count += 1
                else:
                    skipped_count += 1

            except Client.DoesNotExist:
                print(f"[ERROR] Project '{project.name}' references non-existent client: {project.client_username}")
                print()
                error_count += 1
        else:
            skipped_count += 1

    print(f"{'='*60}")
    print("SYNC COMPLETE")
    print(f"{'='*60}\n")

    print(f"Summary:")
    print(f"- Projects updated: {updated_count}")
    print(f"- Projects already in sync: {skipped_count}")
    print(f"- Errors: {error_count}")
    print()

    if updated_count > 0:
        print("[SUCCESS] Project emails have been synced with Client model!")
        print("The reports page should now show the correct emails.")
    else:
        print("[INFO] No updates needed - all emails are already in sync.")

    print(f"\n{'='*60}\n")

if __name__ == '__main__':
    response = input("This will update project emails to match the Client model. Continue? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        sync_all_emails()
    else:
        print("Operation cancelled.")
