"""
Check which projects Ethan is assigned to.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import Client, Project

def check_ethan_projects():
    """Check Ethan's project assignments"""
    username = 'Ethan'

    try:
        client = Client.objects.get(username=username)
        print(f"[OK] Found client: {client.username} ({client.email})")
        print()

        # Check projects via ManyToMany relationship
        assigned_projects = client.projects.all()
        
        print("=" * 60)
        print("PROJECTS VIA MANYTOMANY (New Method)")
        print("=" * 60)
        if assigned_projects.exists():
            for project in assigned_projects:
                print(f"  - {project.name} (ID: {project.id}, Status: {project.status})")
        else:
            print("  (No projects assigned via ManyToMany)")
        
        # Check projects via email matching (old method)
        print()
        print("=" * 60)
        print("PROJECTS VIA EMAIL MATCH (Old Method)")
        print("=" * 60)
        email_projects = Project.objects.filter(client_email=client.email)
        if email_projects.exists():
            for project in email_projects:
                print(f"  - {project.name} (ID: {project.id}, Status: {project.status})")
        else:
            print("  (No projects found with matching email)")

        # Show all available projects
        print()
        print("=" * 60)
        print("ALL AVAILABLE PROJECTS")
        print("=" * 60)
        all_projects = Project.objects.all()
        if all_projects.exists():
            for project in all_projects:
                print(f"  - {project.name} (ID: {project.id})")
                print(f"    Status: {project.status}")
                print(f"    Client Email: {project.client_email}")
                assigned_clients = project.clients.all()
                if assigned_clients.exists():
                    print(f"    Assigned Clients: {', '.join([c.username for c in assigned_clients])}")
                else:
                    print(f"    Assigned Clients: (none)")
                print()
        else:
            print("  (No projects in database)")

    except Client.DoesNotExist:
        print(f"[FAIL] Client '{username}' not found")

if __name__ == "__main__":
    print("=" * 60)
    print("Checking Ethan's Project Assignments")
    print("=" * 60)
    print()

    check_ethan_projects()
