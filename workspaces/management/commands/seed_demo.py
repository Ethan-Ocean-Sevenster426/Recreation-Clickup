"""
Usage:
    python manage.py seed_demo

Creates realistic demo data:
  - 43 users (including the existing admin)
  - 4 Organisations (Workspaces in the UI)
  - 27 Spaces distributed across the 4 orgs
  - Lists, tasks, subtasks, time entries, and comments spread
    across a 2-year window ending today.
"""
import random
from datetime import date, timedelta, datetime, timezone as dt_tz

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from workspaces.models import (
    Organization, Workspace, WorkspaceMember,
    TaskList, TaskStatus, Task, Subtask, TaskComment, TimeEntry,
    DEFAULT_STATUSES,
)

User = get_user_model()

# ── Seed data pools ──────────────────────────────────────────────────────────

FIRST_NAMES = [
    "Alice", "Bob", "Carol", "David", "Emma", "Frank", "Grace", "Henry",
    "Iris", "James", "Karen", "Liam", "Mia", "Noah", "Olivia", "Paul",
    "Quinn", "Rachel", "Sam", "Tina", "Uma", "Victor", "Wendy", "Xander",
    "Yara", "Zoe", "Aaron", "Beth", "Chris", "Diana", "Evan", "Fiona",
    "George", "Hannah", "Ivan", "Julia", "Kevin", "Laura", "Mike", "Nina",
    "Oscar", "Petra",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams",
]

ORGS = [
    "Acme Engineering",
    "Design Studio",
    "Operations Hub",
    "Client Services",
]

# (org_index, space_name, color)
SPACES = [
    # Acme Engineering — 8 spaces
    (0, "Backend Platform",   "purple"),
    (0, "Frontend Web",       "blue"),
    (0, "Mobile Apps",        "pink"),
    (0, "DevOps & Infra",     "orange"),
    (0, "QA & Testing",       "red"),
    (0, "Security",           "gray"),
    (0, "Data Engineering",   "green"),
    (0, "API Integrations",   "blue"),
    # Design Studio — 7 spaces
    (1, "Brand & Identity",   "pink"),
    (1, "Product UX",         "purple"),
    (1, "Marketing Assets",   "orange"),
    (1, "Motion & Video",     "red"),
    (1, "Design Systems",     "blue"),
    (1, "User Research",      "green"),
    (1, "Illustration",       "yellow"),
    # Operations Hub — 7 spaces
    (2, "HR & Recruiting",    "green"),
    (2, "Finance",            "blue"),
    (2, "Legal & Compliance", "gray"),
    (2, "IT Support",         "orange"),
    (2, "Facilities",         "purple"),
    (2, "Vendor Management",  "red"),
    (2, "Analytics & BI",     "blue"),
    # Client Services — 5 spaces
    (3, "Onboarding",         "green"),
    (3, "Account Management", "blue"),
    (3, "Support Tickets",    "red"),
    (3, "Renewals",           "orange"),
    (3, "Client Projects",    "purple"),
]

LIST_TEMPLATES = {
    "Backend Platform":   ["Core API", "Auth Service", "Microservices", "Database Ops", "Bug Fixes"],
    "Frontend Web":       ["Component Library", "Page Builds", "Performance", "Accessibility", "Bug Fixes"],
    "Mobile Apps":        ["iOS", "Android", "Cross-Platform", "App Store", "Bug Fixes"],
    "DevOps & Infra":     ["CI/CD", "Cloud Resources", "Monitoring", "Disaster Recovery", "Security Patches"],
    "QA & Testing":       ["Test Plans", "Regression", "Automation", "Performance Tests", "Sign-Off"],
    "Security":           ["Vulnerability Mgmt", "Audits", "Pen Tests", "Compliance", "Incident Response"],
    "Data Engineering":   ["Pipelines", "Warehousing", "ML Features", "Data Quality", "Reporting"],
    "API Integrations":   ["3rd Party APIs", "Webhooks", "SDK", "Documentation", "Breaking Changes"],
    "Brand & Identity":   ["Logo & Marks", "Brand Guidelines", "Typography", "Color System", "Assets"],
    "Product UX":         ["Wireframes", "Prototypes", "Design Reviews", "Handoff", "Usability"],
    "Marketing Assets":   ["Campaigns", "Social Media", "Email Templates", "Landing Pages", "Print"],
    "Motion & Video":     ["Explainer Videos", "Social Reels", "Animations", "Post-Production", "Delivery"],
    "Design Systems":     ["Components", "Documentation", "Tokens", "Storybook", "Reviews"],
    "User Research":      ["Interviews", "Surveys", "Usability Studies", "Analysis", "Reports"],
    "Illustration":       ["Icons", "Infographics", "Custom Artwork", "Style Guides", "Delivery"],
    "HR & Recruiting":    ["Open Roles", "Interviews", "Onboarding", "Benefits", "Policy Updates"],
    "Finance":            ["Budgeting", "Invoicing", "Payroll", "Reporting", "Audits"],
    "Legal & Compliance": ["Contracts", "Regulatory", "IP & Patents", "Privacy", "Disputes"],
    "IT Support":         ["Hardware", "Software Licenses", "Access Requests", "Tickets", "Infrastructure"],
    "Facilities":         ["Office Maintenance", "Supplies", "Events", "Health & Safety", "Vendors"],
    "Vendor Management":  ["RFPs", "Contracts", "Performance Reviews", "Renewals", "Onboarding"],
    "Analytics & BI":     ["Dashboards", "Data Sources", "Reports", "KPIs", "Ad-Hoc Analysis"],
    "Onboarding":         ["New Clients", "Setup Checklists", "Training", "Go-Live", "Follow-Up"],
    "Account Management": ["Health Checks", "QBRs", "Escalations", "Expansions", "Churn Risk"],
    "Support Tickets":    ["Open", "In Progress", "Escalated", "Resolved", "Knowledge Base"],
    "Renewals":           ["At Risk", "Upcoming", "Negotiating", "Closed Won", "Closed Lost"],
    "Client Projects":    ["Discovery", "Design", "Development", "UAT", "Launch"],
}

TASK_VERBS = [
    "Implement", "Design", "Review", "Fix", "Refactor", "Write", "Update",
    "Create", "Deploy", "Test", "Migrate", "Optimize", "Document", "Audit",
    "Investigate", "Resolve", "Configure", "Integrate", "Analyse", "Plan",
    "Research", "Build", "Improve", "Monitor", "Validate", "Automate",
    "Schedule", "Draft", "Publish", "Archive",
]

TASK_NOUNS = [
    "authentication flow", "user dashboard", "API endpoint", "CI pipeline",
    "database schema", "error handling", "logging system", "test suite",
    "cache layer", "data model", "onboarding email", "permission matrix",
    "rate limiter", "payment integration", "notification service",
    "search index", "export feature", "import tool", "audit trail",
    "backup procedure", "SSL certificate", "staging environment",
    "performance benchmark", "A/B test", "analytics event", "webhook handler",
    "dark mode styles", "accessibility fixes", "mobile layout", "SEO tags",
    "design tokens", "icon set", "PDF export", "Slack integration",
    "customer portal", "admin panel", "usage report", "cost forecast",
    "vendor SLA", "HR policy", "security patch", "data pipeline",
    "client handoff", "launch checklist", "knowledge article",
]

COMMENT_BODIES = [
    "Looking into this now, should have an update by EOD.",
    "Blocked on input from the design team — following up.",
    "Done! Deployed to staging for review.",
    "This needs a second look — edge case found during testing.",
    "Merged the PR, waiting for CI to pass.",
    "Can we move the deadline? Still waiting on dependencies.",
    "Spoke with the client — they approved the approach.",
    "Added unit tests; coverage at 87 %.",
    "Updated the spec doc, link in the description.",
    "Ready for code review.",
    "Assigned to me — will pick this up after stand-up.",
    "Closed — resolved in the latest release.",
    "Needs more context. Can someone clarify the acceptance criteria?",
    "Running load tests overnight, will share results tomorrow.",
    "Hotfix shipped to production at 14:32 UTC.",
]

SUBTASK_TEMPLATES = [
    ["Draft spec", "Get approval", "Implement", "Write tests", "Deploy"],
    ["Research options", "Prototype", "Review with team", "Finalise"],
    ["Create ticket", "Investigate", "Fix", "Verify in staging"],
    ["Gather requirements", "Design mockup", "Build", "QA", "Sign-off"],
    ["Plan", "Execute", "Monitor", "Close"],
]

PRIORITY_WEIGHTS = [
    ("low", 20), ("normal", 45), ("high", 25), ("urgent", 10),
]


def weighted_choice(options):
    choices, weights = zip(*options)
    total = sum(weights)
    r = random.randint(1, total)
    acc = 0
    for c, w in zip(choices, weights):
        acc += w
        if r <= acc:
            return c
    return choices[-1]


def rand_dt(start: date, end: date) -> datetime:
    """Random naive datetime between two dates, converted to UTC-aware."""
    delta = (end - start).days
    d = start + timedelta(days=random.randint(0, max(delta, 0)))
    h, m = random.randint(8, 18), random.randint(0, 59)
    naive = datetime(d.year, d.month, d.day, h, m)
    return naive.replace(tzinfo=dt_tz.utc)


class Command(BaseCommand):
    help = "Seed the database with 2-year demo data (43 users, 4 orgs, 27 spaces)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush", action="store_true",
            help="Delete ALL existing workspace data before seeding (keeps the admin user).",
        )

    def handle(self, *args, **options):
        rng = random.Random(42)  # deterministic seed

        if options["flush"]:
            self.stdout.write("Flushing existing workspace data…")
            TimeEntry.objects.all().delete()
            TaskComment.objects.all().delete()
            Subtask.objects.all().delete()
            Task.objects.all().delete()
            TaskStatus.objects.all().delete()
            TaskList.objects.all().delete()
            WorkspaceMember.objects.all().delete()
            Workspace.objects.all().delete()
            Organization.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        today = date.today()
        two_years_ago = today - timedelta(days=730)

        # ── 1. Users ─────────────────────────────────────────────────────────
        self.stdout.write("Creating users…")
        admin = User.objects.filter(is_staff=True).first()
        if not admin:
            admin = User.objects.create_superuser("admin", "admin@luma.dev", "admin123")

        users = [admin]
        target = 43
        existing_usernames = set(User.objects.values_list("username", flat=True))

        for i in range(target - 1):
            fn = rng.choice(FIRST_NAMES)
            ln = rng.choice(LAST_NAMES)
            username = f"{fn.lower()}.{ln.lower()}{i}"
            if username in existing_usernames:
                username = f"{fn.lower()}{i}{rng.randint(10,99)}"
            existing_usernames.add(username)
            role = rng.choices(
                ["employee", "manager", "admin"],
                weights=[70, 22, 8], k=1
            )[0]
            u, created = User.objects.get_or_create(
                username=username,
                defaults=dict(
                    first_name=fn, last_name=ln,
                    email=f"{username}@luma.dev",
                    role=role,
                    is_staff=(role == "admin"),
                )
            )
            if created:
                u.set_password("password123")
                u.save()
            users.append(u)

        self.stdout.write(f"  -> {len(users)} users ready.")

        # ── 2. Organisations ─────────────────────────────────────────────────
        self.stdout.write("Creating organisations…")
        org_objects = []
        for org_name in ORGS:
            org, _ = Organization.objects.get_or_create(
                name=org_name,
                defaults={"owner": admin},
            )
            org_objects.append(org)

        # ── 3. Spaces ─────────────────────────────────────────────────────────
        self.stdout.write("Creating spaces (Workspaces) …")
        space_objects = []
        for org_idx, space_name, color in SPACES:
            org = org_objects[org_idx]
            # pick a random owner from the user pool
            owner = rng.choice(users[:20])
            ws, _ = Workspace.objects.get_or_create(
                name=space_name,
                organization=org,
                defaults={"owner": owner, "purpose": "work"},
            )
            space_objects.append(ws)

            # Add 5-15 members
            member_pool = rng.sample(users, k=rng.randint(5, 15))
            for mu in member_pool:
                WorkspaceMember.objects.get_or_create(
                    workspace=ws, user=mu,
                    defaults={"role": rng.choice(["editor", "editor", "viewer"])},
                )
            if not WorkspaceMember.objects.filter(workspace=ws, user=owner).exists():
                WorkspaceMember.objects.create(workspace=ws, user=owner, role="editor")

        self.stdout.write(f"  -> {len(space_objects)} spaces ready.")

        # ── 4. Lists, Statuses, Tasks, Subtasks, Comments, Time entries ───────
        self.stdout.write("Creating lists, tasks, and activity data…")

        total_tasks = 0
        total_entries = 0

        for ws in space_objects:
            list_names = LIST_TEMPLATES.get(ws.name, ["General", "Backlog", "In Review", "Done"])
            ws_members = list(ws.memberships.values_list("user_id", flat=True))
            ws_users = [u for u in users if u.pk in ws_members]
            if not ws_users:
                ws_users = [admin]

            for list_name in list_names:
                tl, _ = TaskList.objects.get_or_create(
                    workspace=ws, name=list_name,
                    defaults={"color": rng.choice(["blue", "purple", "green", "orange", "red", "pink"]),
                              "icon": rng.choice(["L", "P", "G", "T", "R", "B", "S", "I"])},
                )

                # Ensure statuses exist
                if not tl.statuses.exists():
                    for key, name, color, pos, is_done in DEFAULT_STATUSES:
                        TaskStatus.objects.get_or_create(
                            task_list=tl, key=key,
                            defaults={"name": name, "color": color, "position": pos, "is_done": is_done},
                        )

                statuses = list(tl.statuses.all())
                status_keys = [s.key for s in statuses]

                # 15-40 tasks per list, created over 2 years
                n_tasks = rng.randint(15, 40)
                for _ in range(n_tasks):
                    verb = rng.choice(TASK_VERBS)
                    noun = rng.choice(TASK_NOUNS)
                    title = f"{verb} {noun}"

                    created_date = two_years_ago + timedelta(days=rng.randint(0, 730))
                    due_offset = rng.randint(3, 30)
                    due_date = created_date + timedelta(days=due_offset) if rng.random() > 0.25 else None
                    start_date = created_date if rng.random() > 0.5 else None

                    priority = weighted_choice(PRIORITY_WEIGHTS)
                    status_key = rng.choice(status_keys)
                    task = Task.objects.create(
                        workspace=ws,
                        task_list=tl,
                        title=title,
                        description=f"Auto-generated task: {title}." if rng.random() > 0.4 else "",
                        status=status_key,
                        priority=priority,
                        start_date=start_date,
                        due_date=due_date,
                        created_by=rng.choice(ws_users),
                        estimated_minutes=rng.choice([None, 30, 60, 90, 120, 180, 240, 480])
                    )
                    # Assign 1-3 random users
                    if rng.random() > 0.15:
                        n = rng.randint(1, min(3, len(ws_users)))
                        task.assignees.set(rng.sample(ws_users, n))

                    # Manually set created_at to spread over 2 years
                    Task.objects.filter(pk=task.pk).update(
                        created_at=rand_dt(two_years_ago, today)
                    )

                    total_tasks += 1

                    # Subtasks (40 % of tasks)
                    if rng.random() < 0.4:
                        template = rng.choice(SUBTASK_TEMPLATES)
                        for st_title in template:
                            st = Subtask.objects.create(
                                task=task,
                                title=st_title,
                                is_done=rng.random() > 0.5,
                            )
                            n = rng.randint(0, min(2, len(ws_users)))
                            if n:
                                st.assignees.set(rng.sample(ws_users, n))

                    # Comments (50 % of tasks, 1-4 comments)
                    if rng.random() < 0.5:
                        for _ in range(rng.randint(1, 4)):
                            c_date = rand_dt(two_years_ago, today)
                            c = TaskComment(
                                task=task,
                                author=rng.choice(ws_users),
                                body=rng.choice(COMMENT_BODIES),
                            )
                            c.save()
                            TaskComment.objects.filter(pk=c.pk).update(created_at=c_date)

                    # Time entries (60 % of tasks, 1-6 entries)
                    if rng.random() < 0.6:
                        for _ in range(rng.randint(1, 6)):
                            duration_minutes = rng.randint(15, 240)
                            start_dt = rand_dt(two_years_ago, today)
                            end_dt = start_dt + timedelta(minutes=duration_minutes)
                            TimeEntry.objects.create(
                                task=task,
                                user=rng.choice(ws_users),
                                started_at=start_dt,
                                ended_at=end_dt,
                                is_manual=True,
                            )
                            total_entries += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nOK Seed complete!\n"
                f"  Users:        {User.objects.count()}\n"
                f"  Organisations: {Organization.objects.count()}\n"
                f"  Spaces:       {Workspace.objects.count()}\n"
                f"  Lists:        {TaskList.objects.count()}\n"
                f"  Tasks:        {total_tasks}\n"
                f"  Time entries: {total_entries}\n"
            )
        )
