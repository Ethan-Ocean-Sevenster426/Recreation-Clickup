"""
Helper script to add multiple clients/investors to a project.

This script demonstrates how to use the new multi-client feature where
one project can have multiple clients (investors) who can each login
and see their project information.

Usage:
    python add_clients_to_project.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import Project, Client

def add_clients_to_project(project_id, client_usernames):
    """
    Add multiple clients to a project.

    Args:
        project_id: The ID of the project
        client_usernames: List of client usernames to add
    """
    try:
        project = Project.objects.get(id=project_id)
        print(f"[OK] Found project: {project.name}")

        added_clients = []
        for username in client_usernames:
            try:
                client = Client.objects.get(username=username)
                # Add client to the project (if not already added)
                if not project.clients.filter(id=client.id).exists():
                    project.clients.add(client)
                    added_clients.append(username)
                    print(f"[OK] Added client: {username}")
                else:
                    print(f"[INFO] Client already associated: {username}")
            except Client.DoesNotExist:
                print(f"[FAIL] Client not found: {username}")

        if added_clients:
            print(f"\n[SUCCESS] Added {len(added_clients)} client(s) to project '{project.name}'")
            print(f"Clients can now login and view this project:")
            for username in added_clients:
                print(f"  - {username}")
        else:
            print(f"\n[INFO] No new clients were added to '{project.name}'")

    except Project.DoesNotExist:
        print(f"[FAIL] Project with ID {project_id} not found")


def list_project_clients(project_id):
    """List all clients associated with a project."""
    try:
        project = Project.objects.get(id=project_id)
        clients = project.clients.all()

        print(f"\nProject: {project.name}")
        print(f"Associated Clients/Investors ({clients.count()}):")

        if clients.exists():
            for client in clients:
                print(f"  - {client.username} ({client.email})")
        else:
            print("  (No clients associated via new multi-client system)")
            print(f"  Legacy client field: {project.client} ({project.client_email})")

    except Project.DoesNotExist:
        print(f"[FAIL] Project with ID {project_id} not found")


def show_client_projects(client_username):
    """Show all projects a client has access to."""
    try:
        client = Client.objects.get(username=client_username)
        projects = client.projects.all()

        print(f"\nClient: {client.username} ({client.email})")
        print(f"Accessible Projects ({projects.count()}):")

        if projects.exists():
            for project in projects:
                print(f"  - {project.name} (ID: {project.id}, Status: {project.status})")
        else:
            print("  (No projects associated)")

    except Client.DoesNotExist:
        print(f"[FAIL] Client '{client_username}' not found")


if __name__ == "__main__":
    print("=" * 60)
    print("Multi-Client Project Management Helper")
    print("=" * 60)

    # Example usage - modify these values as needed

    # Example 1: Add multiple clients to a project
    print("\nExample 1: Add multiple clients/investors to a project")
    print("-" * 60)
    # Uncomment and modify the line below:
    # add_clients_to_project(project_id=3, client_usernames=['CBH-Tigane', 'investor2', 'investor3'])
    print("To add clients to a project, uncomment and modify the line above")

    # Example 2: List all clients associated with a project
    print("\n\nExample 2: List all clients for a project")
    print("-" * 60)
    # Uncomment and modify the line below:
    # list_project_clients(project_id=3)
    print("To list project clients, uncomment and modify the line above")

    # Example 3: Show all projects a client can access
    print("\n\nExample 3: Show all projects for a client")
    print("-" * 60)
    # Uncomment and modify the line below:
    # show_client_projects(client_username='CBH-Tigane')
    print("To show client projects, uncomment and modify the line above")

    print("\n" + "=" * 60)
    print("Note: You can also use the Django admin interface to add")
    print("multiple clients to projects using the 'Clients' field.")
    print("=" * 60)
