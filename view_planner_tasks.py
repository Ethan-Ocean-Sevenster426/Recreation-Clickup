"""
View Microsoft Planner Tasks
Simple script to fetch and display tasks from Microsoft Planner
"""

import requests
import json
from msal import ConfidentialClientApplication

# Azure AD App Configuration
CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
TENANT_ID = 'YOUR_TENANT_ID'

# Microsoft Graph API endpoint
GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'

def get_access_token():
    """Get access token using client credentials flow"""
    authority = f'https://login.microsoftonline.com/{TENANT_ID}'

    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=authority,
        client_credential=CLIENT_SECRET,
    )

    # Get token
    result = app.acquire_token_for_client(scopes=['https://graph.microsoft.com/.default'])

    if 'access_token' in result:
        return result['access_token']
    else:
        raise Exception(f"Error getting token: {result.get('error_description')}")

def get_planner_plans(token):
    """Get all planner plans"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Get groups (plans are associated with groups)
    response = requests.get(
        f'{GRAPH_API_ENDPOINT}/me/planner/plans',
        headers=headers
    )

    if response.status_code == 200:
        return response.json().get('value', [])
    else:
        print(f"Error getting plans: {response.status_code}")
        print(response.text)
        return []

def get_plan_tasks(token, plan_id):
    """Get all tasks for a specific plan"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(
        f'{GRAPH_API_ENDPOINT}/planner/plans/{plan_id}/tasks',
        headers=headers
    )

    if response.status_code == 200:
        return response.json().get('value', [])
    else:
        print(f"Error getting tasks: {response.status_code}")
        print(response.text)
        return []

def display_tasks():
    """Main function to display all tasks"""
    try:
        # Get access token
        print("Getting access token...")
        token = get_access_token()
        print("✓ Token acquired")

        # Get plans
        print("\nFetching plans...")
        plans = get_planner_plans(token)
        print(f"✓ Found {len(plans)} plan(s)")

        if not plans:
            print("No plans found!")
            return

        # Display tasks for each plan
        for plan in plans:
            plan_name = plan.get('title', 'Unnamed Plan')
            plan_id = plan.get('id')

            print(f"\n{'='*60}")
            print(f"PLAN: {plan_name}")
            print(f"{'='*60}")

            # Get tasks for this plan
            tasks = get_plan_tasks(token, plan_id)

            if not tasks:
                print("  No tasks in this plan")
                continue

            # Display each task
            for i, task in enumerate(tasks, 1):
                title = task.get('title', 'Untitled')
                percent_complete = task.get('percentComplete', 0)
                due_date = task.get('dueDateTime', 'No due date')
                priority = task.get('priority', 5)

                # Status
                if percent_complete == 100:
                    status = "✓ COMPLETED"
                elif percent_complete > 0:
                    status = f"◐ IN PROGRESS ({percent_complete}%)"
                else:
                    status = "○ NOT STARTED"

                # Priority
                priority_label = {
                    1: "🔴 URGENT",
                    3: "🟠 HIGH",
                    5: "🟡 NORMAL",
                    9: "🟢 LOW"
                }.get(priority, "⚪ UNKNOWN")

                print(f"\n  [{i}] {title}")
                print(f"      Status: {status}")
                print(f"      Priority: {priority_label}")
                print(f"      Due: {due_date}")

        print(f"\n{'='*60}")
        print("DONE")
        print(f"{'='*60}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("MICROSOFT PLANNER TASKS VIEWER")
    print("=" * 60)

    # Check if credentials are set
    if CLIENT_ID == 'YOUR_CLIENT_ID':
        print("\n❌ ERROR: You need to configure Azure AD credentials first!")
        print("\nSTEPS TO CONFIGURE:")
        print("1. Go to https://portal.azure.com")
        print("2. Navigate to 'Azure Active Directory' > 'App registrations'")
        print("3. Click 'New registration'")
        print("4. Name it 'Planner Tasks Viewer'")
        print("5. After creation, copy these values:")
        print("   - Application (client) ID")
        print("   - Directory (tenant) ID")
        print("6. Go to 'Certificates & secrets' > 'New client secret'")
        print("7. Copy the secret value")
        print("8. Go to 'API permissions' > 'Add a permission'")
        print("9. Select 'Microsoft Graph' > 'Application permissions'")
        print("10. Add these permissions:")
        print("    - Tasks.Read.All or Tasks.ReadWrite.All")
        print("    - Group.Read.All")
        print("11. Click 'Grant admin consent'")
        print("\n12. Update this script with your credentials:")
        print("    CLIENT_ID = 'your-client-id'")
        print("    CLIENT_SECRET = 'your-client-secret'")
        print("    TENANT_ID = 'your-tenant-id'")
    else:
        display_tasks()
