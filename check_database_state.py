#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from home.models import Project, Client, Task, SubTask, TaskComment, SubTaskComment, ClientOTP

def check_database_state():
    print("=== DATABASE STATE CHECK ===")
    print()
    
    # Count records
    project_count = Project.objects.count()
    client_count = Client.objects.count()
    task_count = Task.objects.count()
    subtask_count = SubTask.objects.count()
    task_comment_count = TaskComment.objects.count()
    subtask_comment_count = SubTaskComment.objects.count()
    client_otp_count = ClientOTP.objects.count()
    
    print(f"📊 RECORD COUNTS:")
    print(f"   Projects: {project_count}")
    print(f"   Clients: {client_count}")
    print(f"   Tasks: {task_count}")
    print(f"   Subtasks: {subtask_count}")
    print(f"   Task Comments: {task_comment_count}")
    print(f"   SubTask Comments: {subtask_comment_count}")
    print(f"   Client OTPs: {client_otp_count}")
    print()
    
    # Show recent projects
    if project_count > 0:
        print("📋 RECENT PROJECTS:")
        recent_projects = Project.objects.order_by('-created_at')[:5]
        for project in recent_projects:
            print(f"   - {project.name} (Client: {project.client}, Status: {project.status})")
        print()
    
    # Show recent clients
    if client_count > 0:
        print("👥 RECENT CLIENTS:")
        recent_clients = Client.objects.order_by('-created_at')[:5]
        for client in recent_clients:
            print(f"   - {client.username} ({client.email})")
        print()
    
    # Show problematic data
    print("🔍 POTENTIAL ISSUES:")
    
    # Check for duplicate usernames
    from django.db.models import Count
    duplicate_usernames = Client.objects.values('username').annotate(count=Count('username')).filter(count__gt=1)
    if duplicate_usernames:
        print(f"   ⚠️  Found {len(duplicate_usernames)} duplicate usernames")
        for dup in duplicate_usernames:
            print(f"      - Username '{dup['username']}' appears {dup['count']} times")
    else:
        print("   ✅ No duplicate usernames found")
    
    # Check for duplicate emails
    duplicate_emails = Client.objects.values('email').annotate(count=Count('email')).filter(count__gt=1)
    if duplicate_emails:
        print(f"   ⚠️  Found {len(duplicate_emails)} duplicate emails")
        for dup in duplicate_emails:
            print(f"      - Email '{dup['email']}' appears {dup['count']} times")
    else:
        print("   ✅ No duplicate emails found")
    
    # Check for projects without tasks
    projects_without_tasks = Project.objects.filter(tasks__isnull=True)
    if projects_without_tasks.exists():
        print(f"   ⚠️  Found {projects_without_tasks.count()} projects without tasks")
    else:
        print("   ✅ All projects have tasks")
    
    print()
    print("=== END DATABASE STATE CHECK ===")

if __name__ == "__main__":
    check_database_state()
