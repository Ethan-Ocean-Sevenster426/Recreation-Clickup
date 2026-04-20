"""
View Microsoft Planner Tasks - Simple Version
Uses your personal Microsoft 365 login (no app registration needed)
"""

import requests
import webbrowser
from msal import PublicClientApplication

# Public client ID for Microsoft Graph (no secret needed)
CLIENT_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e"  # Microsoft Graph Explorer public client

AUTHORITY = "https://login.microsoftonline.com/common"
SCOPES = [
    "Tasks.Read",
    "Group.Read.All",
    "User.Read"
]

GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'

def get_access_token():
    """Get access token using interactive browser login"""
    app = PublicClientApplication(
        CLIENT_ID,
        authority=AUTHORITY
    )

    # Try to get token from cache first
    accounts = app.get_accounts()
    if accounts:
        print("Found cached account, attempting silent login...")
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and 'access_token' in result:
            return result['access_token']

    # Interactive login
    print("\nOpening browser for Microsoft login...")
    print("Please sign in with your Microsoft 365 account")

    result = app.acquire_token_interactive(
        scopes=SCOPES,
        prompt='select_account'
    )

    if 'access_token' in result:
        print("✓ Successfully logged in!")
        return result['access_token']
    else:
        raise Exception(f"Login failed: {result.get('error_description')}")

def get_my_tasks(token):
    """Get all tasks for the current user"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Get user's planner tasks
    response = requests.get(
        f'{GRAPH_API_ENDPOINT}/me/planner/tasks',
        headers=headers
    )

    if response.status_code == 200:
        return response.json().get('value', [])
    else:
        print(f"Error getting tasks: {response.status_code}")
        print(response.text)
        return []

def get_plan_details(token, plan_id):
    """Get plan details"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(
        f'{GRAPH_API_ENDPOINT}/planner/plans/{plan_id}',
        headers=headers
    )

    if response.status_code == 200:
        return response.json()
    else:
        return None

def display_tasks():
    """Main function to display all tasks"""
    try:
        # Get access token (will open browser)
        token = get_access_token()

        # Get all tasks
        print("\nFetching your planner tasks...")
        tasks = get_my_tasks(token)

        if not tasks:
            print("✓ No tasks found!")
            return

        print(f"✓ Found {len(tasks)} task(s)\n")

        # Group tasks by plan
        plans = {}
        for task in tasks:
            plan_id = task.get('planId')
            if plan_id not in plans:
                plans[plan_id] = {
                    'name': None,
                    'tasks': []
                }
            plans[plan_id]['tasks'].append(task)

        # Get plan names and display
        for plan_id, plan_data in plans.items():
            # Get plan name
            plan_details = get_plan_details(token, plan_id)
            plan_name = plan_details.get('title', 'Unknown Plan') if plan_details else 'Unknown Plan'

            print(f"\n{'='*70}")
            print(f"📋 PLAN: {plan_name}")
            print(f"{'='*70}")

            # Display tasks
            for i, task in enumerate(plan_data['tasks'], 1):
                title = task.get('title', 'Untitled')
                percent_complete = task.get('percentComplete', 0)
                due_date = task.get('dueDateTime', 'No due date')
                priority = task.get('priority', 5)
                bucket_id = task.get('bucketId', '')

                # Format due date
                if due_date != 'No due date':
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                        due_date = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        pass

                # Status
                if percent_complete == 100:
                    status = "✅ COMPLETED"
                elif percent_complete > 0:
                    status = f"🔄 IN PROGRESS ({percent_complete}%)"
                else:
                    status = "⭕ NOT STARTED"

                # Priority
                priority_label = {
                    1: "🔴 URGENT",
                    3: "🟠 HIGH",
                    5: "🟡 MEDIUM",
                    9: "🟢 LOW"
                }.get(priority, "⚪ NORMAL")

                print(f"\n  {i}. {title}")
                print(f"     Status: {status}")
                print(f"     Priority: {priority_label}")
                print(f"     Due: {due_date}")

        print(f"\n{'='*70}")
        print(f"✓ TOTAL: {len(tasks)} task(s)")
        print(f"{'='*70}\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 70)
    print("MICROSOFT PLANNER TASKS VIEWER")
    print("=" * 70)
    print("\nOpening browser to sign in with Microsoft 365...")
    print("No app registration needed - uses your personal login\n")

    display_tasks()
