#!/usr/bin/env python
"""
One-time ClickUp to Luma import script.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, date

# ── Django bootstrap ────────────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eclick.settings")

import django
django.setup()

from django.contrib.auth import get_user_model
from workspaces.models import (
    Organization, Workspace, TaskList, TaskStatus,
    Task, Subtask, TaskComment, WorkspaceMember, Category,
)

User = get_user_model()

# ── Config ──────────────────────────────────────────────────────────
API_KEY = "pk_99695205_9XO1FM230GW0Z9VX6SUQFY11ALKBIH9Y"
TEAM_ID = "90121464969"
BASE    = "https://api.clickup.com/api/v2"
HEADERS = {"Authorization": API_KEY}

# ── Helpers ─────────────────────────────────────────────────────────
def api(path, params=None):
    """GET from ClickUp API with simple rate-limit handling."""
    url = f"{BASE}/{path.lstrip('/')}"
    for attempt in range(5):
        r = requests.get(url, headers=HEADERS, params=params or {})
        if r.status_code == 429:
            wait = int(r.headers.get("Retry-After", 2))
            print(f"  rate-limited, waiting {wait}s ...")
            time.sleep(wait)
            continue
        if r.status_code != 200:
            print(f"  API error {r.status_code}: {r.text[:200]}")
            r.raise_for_status()
        return r.json()
    raise RuntimeError(f"Too many retries for {url}")


def ts_to_date(ms):
    """ClickUp millisecond timestamp → Python date, or None."""
    if not ms:
        return None
    return datetime.utcfromtimestamp(int(ms) / 1000).date()


def ts_to_datetime(ms):
    """ClickUp millisecond timestamp → Python datetime, or None."""
    if not ms:
        return None
    return datetime.utcfromtimestamp(int(ms) / 1000)


PRIORITY_MAP = {
    "1": "urgent",  "urgent": "urgent",
    "2": "high",    "high":   "high",
    "3": "normal",  "normal": "normal",
    "4": "low",     "low":    "low",
}

STATUS_MAP = {
    "to do":             "todo",
    "in progress":       "in_progress",
    "on hold / waiting": "on_hold",
    "on hold":           "on_hold",
    "client review":     "review",
    "internal review":   "internal_review",
    "done":              "done",
    "complete":          "done",
}


def map_priority(cu_priority):
    if not cu_priority:
        return "normal"
    key = cu_priority.get("priority", "") if isinstance(cu_priority, dict) else str(cu_priority)
    return PRIORITY_MAP.get(key.lower(), "normal")


def map_status(cu_status_str):
    return STATUS_MAP.get(cu_status_str.lower().strip(), "todo")


# ── 1. Import users ────────────────────────────────────────────────
print("=" * 60)
print("STEP 1: Importing users")
print("=" * 60)

team_data = api("team")
print(f"  API response keys: {list(team_data.keys())}")

# Handle both {"teams": [...]} and {"team": {...}} response formats
if "teams" in team_data:
    team_info = team_info
elif "team" in team_data:
    team_info = team_data["team"]
else:
    print(f"  Unexpected response: {json.dumps(team_data)[:300]}")
    sys.exit(1)

email_to_user = {}

for member in team_info["members"]:
    cu = member["user"]
    email = cu["email"]
    username = cu.get("username") or email.split("@")[0]

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "username": username,
            "first_name": username.split(".")[0].capitalize() if "." in username else username.split(" ")[0],
            "last_name":  username.split(".")[-1].capitalize() if "." in username else (username.split(" ")[-1] if " " in username else ""),
            "is_active": True,
            "can_login": True,
        },
    )
    if created:
        user.set_password("changeme123")
        user.save()
        print(f"  + Created user: {email} (password: changeme123)")
    else:
        print(f"  ~ User exists:  {email}")

    email_to_user[email] = user

# Also index by ClickUp user id for fast lookup
cuid_to_user = {}
for member in team_info["members"]:
    cu = member["user"]
    u = email_to_user.get(cu["email"])
    if u:
        cuid_to_user[cu["id"]] = u

# Pick an owner (the ClickUp workspace owner, i.e. Jané)
owner_email = None
for member in team_info["members"]:
    if member["user"].get("role_key") == "owner":
        owner_email = member["user"]["email"]
        break
owner = email_to_user.get(owner_email) or list(email_to_user.values())[0]
print(f"  Owner for new objects: {owner.email}")

# ── 2. Import spaces → Organization + Workspaces ──────────────────
print()
print("=" * 60)
print("STEP 2: Importing spaces → Organization + Workspaces")
print("=" * 60)

team_name = team_info["name"]
org, created = Organization.objects.get_or_create(
    name=team_name,
    defaults={"owner": owner},
)
print(f"  {'+ Created' if created else '~ Exists'} Organization: {team_name}")

spaces_data = api(f"team/{TEAM_ID}/space", {"archived": "false"})
space_to_workspace = {}

for sp in spaces_data["spaces"]:
    ws, created = Workspace.objects.get_or_create(
        name=sp["name"],
        organization=org,
        defaults={
            "owner": owner,
            "purpose": "retainer",
        },
    )
    space_to_workspace[sp["id"]] = ws
    print(f"  {'+ Created' if created else '~ Exists'} Workspace: {sp['name']}")

    # Add all users as workspace members
    for u in email_to_user.values():
        WorkspaceMember.objects.get_or_create(
            workspace=ws,
            user=u,
            defaults={"role": "editor"},
        )

# ── 3. Import lists → TaskList + TaskStatus ───────────────────────
print()
print("=" * 60)
print("STEP 3: Importing lists → TaskList + TaskStatus")
print("=" * 60)

list_id_to_tasklist = {}

for space_id, ws in space_to_workspace.items():
    lists_data = api(f"space/{space_id}/list", {"archived": "false"})
    for lst in lists_data["lists"]:
        tl, created = TaskList.objects.get_or_create(
            workspace=ws,
            name=lst["name"],
            defaults={"icon": "📋"},
        )
        list_id_to_tasklist[lst["id"]] = tl
        print(f"  {'+ Created' if created else '~ Exists'} List: {lst['name']} (in {ws.name})")

        # Fetch full list details for statuses
        list_detail = api(f"list/{lst['id']}")
        for idx, st in enumerate(list_detail.get("statuses", [])):
            TaskStatus.objects.get_or_create(
                task_list=tl,
                key=st["status"].lower().replace(" ", "_").replace("/", ""),
                defaults={
                    "name": st["status"].title(),
                    "color": st.get("color", "gray").lstrip("#")[:20],
                    "position": idx,
                    "is_done": st.get("type") in ("closed", "done"),
                },
            )

# ── 4. Import tasks ──────────────────────────────────────────────
print()
print("=" * 60)
print("STEP 4: Importing tasks")
print("=" * 60)

cu_task_id_to_task = {}
subtask_records = []  # (cu_task_dict, parent_luma_task)

for cu_list_id, tl in list_id_to_tasklist.items():
    page = 0
    while True:
        data = api(f"list/{cu_list_id}/task", {
            "subtasks": "true",
            "include_closed": "true",
            "page": str(page),
        })
        tasks = data.get("tasks", [])
        if not tasks:
            break

        for t in tasks:
            # Skip subtasks on first pass – collect them
            if t.get("parent"):
                subtask_records.append(t)
                continue

            status_str = t["status"]["status"] if isinstance(t.get("status"), dict) else "todo"
            priority = map_priority(t.get("priority"))
            status = map_status(status_str)

            # Tags
            tags = ",".join(tag["name"] for tag in t.get("tags", []))

            # Time estimate (ClickUp stores in ms)
            est_minutes = None
            if t.get("time_estimate"):
                est_minutes = int(t["time_estimate"]) // 60000

            task, created = Task.objects.get_or_create(
                workspace=tl.workspace,
                task_list=tl,
                title=t["name"],
                defaults={
                    "description": t.get("text_content") or t.get("description") or "",
                    "status": status,
                    "priority": priority,
                    "start_date": ts_to_date(t.get("start_date")),
                    "due_date": ts_to_date(t.get("due_date")),
                    "tags": tags,
                    "estimated_minutes": est_minutes,
                    "created_at": ts_to_datetime(t.get("date_created")) or datetime.utcnow(),
                },
            )

            if created:
                # Creator
                creator_info = t.get("creator", {})
                creator_user = cuid_to_user.get(creator_info.get("id"))
                if creator_user:
                    task.created_by = creator_user
                    task.save(update_fields=["created_by"])

                # Assignees
                for a in t.get("assignees", []):
                    u = cuid_to_user.get(a.get("id"))
                    if u:
                        task.assignees.add(u)

                print(f"  + Task: {t['name'][:60]}")
            else:
                print(f"  ~ Exists: {t['name'][:60]}")

            cu_task_id_to_task[t["id"]] = task

        page += 1
        if len(tasks) < 100:
            break

# ── 5. Import subtasks ───────────────────────────────────────────
print()
print("=" * 60)
print("STEP 5: Importing subtasks")
print("=" * 60)

for st in subtask_records:
    parent_task = cu_task_id_to_task.get(st.get("parent"))
    if not parent_task:
        print(f"  ! Skipping subtask '{st['name'][:50]}' — parent not found")
        continue

    status_str = st["status"]["status"] if isinstance(st.get("status"), dict) else "todo"
    status = map_status(status_str)
    is_done = status == "done"
    priority = map_priority(st.get("priority"))

    sub, created = Subtask.objects.get_or_create(
        task=parent_task,
        title=st["name"],
        defaults={
            "is_done": is_done,
            "status": status,
            "priority": priority,
            "due_date": ts_to_date(st.get("due_date")),
        },
    )
    if created:
        # Assignees
        for a in st.get("assignees", []):
            u = cuid_to_user.get(a.get("id"))
            if u:
                sub.assignees.add(u)
        print(f"  + Subtask: {st['name'][:60]}")
    else:
        print(f"  ~ Exists:  {st['name'][:60]}")

# ── 6. Import comments ──────────────────────────────────────────
print()
print("=" * 60)
print("STEP 6: Importing comments")
print("=" * 60)

for cu_id, task in cu_task_id_to_task.items():
    try:
        data = api(f"task/{cu_id}/comment")
    except Exception as e:
        print(f"  ! Error fetching comments for '{task.title[:40]}': {e}")
        continue

    for c in data.get("comments", []):
        # Build plain text from comment_text parts
        body = c.get("comment_text", "")
        if not body:
            parts = c.get("comment", [])
            body = "".join(p.get("text", "") for p in parts if isinstance(p, dict))

        if not body.strip():
            continue

        author = cuid_to_user.get(c.get("user", {}).get("id"))
        if not author:
            author = owner

        comment_time = ts_to_datetime(c.get("date"))

        _, created = TaskComment.objects.get_or_create(
            task=task,
            body=body,
            author=author,
            defaults={
                "created_at": comment_time or datetime.utcnow(),
            },
        )
        if created:
            print(f"  + Comment on '{task.title[:40]}' by {author.email}")

# ── Done ─────────────────────────────────────────────────────────
print()
print("=" * 60)
print("IMPORT COMPLETE")
print("=" * 60)
print(f"  Users:      {User.objects.count()}")
print(f"  Workspaces: {Workspace.objects.count()}")
print(f"  Lists:      {TaskList.objects.count()}")
print(f"  Tasks:      {Task.objects.count()}")
print(f"  Subtasks:   {Subtask.objects.count()}")
print(f"  Comments:   {TaskComment.objects.count()}")
