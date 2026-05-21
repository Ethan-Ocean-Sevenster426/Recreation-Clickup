import calendar as _cal
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from django.utils import timezone

from django.contrib import messages
from django.db.models import Count, F, Q
from django.db.models.functions import TruncDate

from django.http import JsonResponse
from django.db.models import Max

from .models import (
    CUSTOM_FIELD_TYPES, Category, CustomField, CustomFieldOption,
    CustomFieldPermission, DashboardCard, DEFAULT_CATEGORIES, ListMember,
    Notification, Organization, ReportTemplate, STATUS_COLORS, Subtask, Task,
    TaskComment, TaskCustomFieldValue, TaskList, TaskStatus, TimeEntry,
    ViewPreference, Workspace, WorkspaceMember,
)
from .notifications import notify_task_updated, notify_task_completed, notify_comment_added

User = get_user_model()


def _task_range(task, fallback_today):
    start = task.start_date or task.due_date
    end = task.due_date or task.start_date
    if not start and not end:
        return None, None
    return start, end


def _assign_lanes(bars):
    bars = sorted(bars, key=lambda b: (b['col_start'], b['col_end']))
    lanes = []
    for b in bars:
        placed = False
        for i, lane in enumerate(lanes):
            if all(b['col_start'] >= ex['col_end'] or ex['col_start'] >= b['col_end'] for ex in lane):
                lane.append(b)
                b['lane'] = i
                placed = True
                break
        if not placed:
            b['lane'] = len(lanes)
            lanes.append([b])
    return max(1, len(lanes))


def _accessible_orgs(user):
    """Organizations the user owns OR has access to via space membership.
    Staff/manager users can see ALL organizations."""
    if user.is_staff or user.role == 'manager':
        return Organization.objects.all()
    return Organization.objects.filter(
        Q(owner=user) | Q(spaces__memberships__user=user)
    ).distinct()


def _active_org(request):
    """Return the currently active Organization for the session, auto-selecting if needed."""
    user = request.user
    orgs = _accessible_orgs(user)
    org_id = request.session.get('active_org_id')
    if org_id:
        org = orgs.filter(pk=org_id).first()
        if org:
            return org
    first = orgs.first()
    if first:
        request.session['active_org_id'] = first.pk
    return first


def _accessible_workspaces(user, organization=None):
    """Spaces the user owns OR is a member of, optionally scoped to an Organization.
    Staff/manager users can access ALL workspaces (org filter ignored)."""
    if user.is_staff or user.role == 'manager':
        qs = Workspace.objects.all()
        # Managers see all workspaces regardless of active org
    else:
        qs = Workspace.objects.filter(Q(owner=user) | Q(memberships__user=user)).distinct()
        if organization is not None:
            qs = qs.filter(organization=organization)
    return qs


def _user_role(user, workspace):
    """Returns 'owner', 'editor', 'viewer', or None."""
    if workspace.owner_id == user.id:
        return 'owner'
    m = WorkspaceMember.objects.filter(workspace=workspace, user=user).first()
    return m.role if m else None


def _nav_context(user, active_workspace=None, active_list=None, request=None, active_org=None):
    if request is not None and active_org is None:
        active_org = _active_org(request)
    running = TimeEntry.objects.filter(user=user, ended_at__isnull=True).select_related('task').first()
    nav_spaces = _accessible_workspaces(user, organization=active_org).select_related('organization').prefetch_related('lists')
    # For managers seeing all workspaces, group by org for sidebar display
    is_manager_view = user.is_staff or user.role == 'manager'
    nav_by_org = {}
    if is_manager_view:
        from collections import OrderedDict
        nav_by_org = OrderedDict()
        for ws in nav_spaces.order_by('organization__name', 'name'):
            org = ws.organization
            org_name = org.name if org else 'No Organization'
            if org_name not in nav_by_org:
                org_image_url = ''
                if org and org.image:
                    try:
                        org_image_url = org.image.url
                    except Exception:
                        pass
                nav_by_org[org_name] = {'image_url': org_image_url, 'workspaces': []}
            nav_by_org[org_name]['workspaces'].append(ws)
    return {
        'nav_workspaces': nav_spaces,
        'nav_by_org': nav_by_org,
        'is_manager_view': is_manager_view,
        'nav_organizations': _accessible_orgs(user) if request else Organization.objects.none(),
        'active_workspace': active_workspace,
        'active_list': active_list,
        'active_org': active_org,
        'status_colors': STATUS_COLORS,
        'workspace_purpose_choices': Workspace.PURPOSE_CHOICES,
        'running_timer': running,
        'running_timer_started_iso': running.started_at.isoformat() if running else '',
        'unread_notif_count': Notification.objects.filter(recipient=user, is_read=False).count(),
    }


def _get_workspace_for_user(user, workspace_id, require_edit=False):
    """Return workspace if user has access. Raises 404 if not. If require_edit, denies viewers."""
    ws = get_object_or_404(_accessible_workspaces(user), pk=workspace_id)
    if require_edit:
        role = _user_role(user, ws)
        if role == 'viewer':
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Viewers can't edit this workspace.")
    return ws


def _filter_tasks_for_user(tasks_qs, user):
    """Employees only see tasks assigned to them or created by them.
    Managers/admins/staff see all tasks."""
    if user.is_staff or user.role == 'manager':
        return tasks_qs
    return tasks_qs.filter(Q(assignees=user) | Q(created_by=user)).distinct()


def _columns(task_list, user=None):
    cols = []
    for s in task_list.statuses.all():
        tasks_qs = task_list.tasks.filter(status=s.key, deleted_at__isnull=True).prefetch_related('assignees')
        if user:
            tasks_qs = _filter_tasks_for_user(tasks_qs, user)
        cols.append({
            'status': s,
            'key': s.key,
            'label': s.name,
            'color': s.color,
            'tasks': list(tasks_qs),
        })
    return cols


def _status_choices(task_list):
    return [(s.key, s.name) for s in task_list.statuses.all()]


# Workspaces
@login_required
def workspace_list(request):
    active_org = _active_org(request)
    workspaces = list(_accessible_workspaces(request.user, organization=active_org).prefetch_related('lists'))
    today = date.today()

    all_tasks = _filter_tasks_for_user(Task.objects.filter(workspace__in=workspaces, deleted_at__isnull=True), request.user)
    open_tasks = all_tasks.exclude(status='done')
    my_open = open_tasks.filter(assignees=request.user)
    due_this_week = open_tasks.filter(due_date__gte=today, due_date__lte=today + timedelta(days=7))
    overdue = open_tasks.filter(due_date__lt=today)

    upcoming_qs = (open_tasks
                   .filter(due_date__gte=today, due_date__lte=today + timedelta(days=14))
                   .select_related('task_list', 'workspace').prefetch_related('assignees')
                   .order_by('due_date')[:6])

    recent_tasks = (all_tasks
                    .select_related('task_list', 'workspace').prefetch_related('assignees')
                    .order_by('-created_at')[:5])

    # Time tracked today by current user
    now = timezone.now()
    todays_entries = TimeEntry.objects.filter(
        user=request.user, started_at__date=today,
    )
    time_today_seconds = sum(e.duration_seconds(now) for e in todays_entries)
    h, rem = divmod(time_today_seconds, 3600)
    m = rem // 60
    if h:
        time_today_label = f"{h}h {m}m"
    elif m:
        time_today_label = f"{m}m"
    else:
        time_today_label = '0m'

    # Per-workspace summary for the cards
    workspace_cards = []
    for w in workspaces:
        ws_tasks = all_tasks.filter(workspace=w)
        lists_detail = []
        for tl in w.lists.all():
            tl_tasks = ws_tasks.filter(task_list=tl)
            tl_total = tl_tasks.count()
            tl_done = tl_tasks.filter(status='done').count()
            lists_detail.append({
                'list': tl,
                'total': tl_total,
                'open': tl_total - tl_done,
                'done': tl_done,
                'overdue': tl_tasks.exclude(status='done').filter(due_date__lt=today).count(),
                'done_pct': round((tl_done / tl_total) * 100) if tl_total else 0,
            })
        workspace_cards.append({
            'ws': w,
            'list_count': len(lists_detail),
            'task_count': ws_tasks.count(),
            'open_count': ws_tasks.exclude(status='done').count(),
            'overdue_count': ws_tasks.exclude(status='done').filter(due_date__lt=today).count(),
            'lists_detail': lists_detail,
        })

    return render(request, 'workspaces/list.html', {
        'workspaces': workspaces,
        'workspace_cards': workspace_cards,
        'upcoming_tasks': upcoming_qs,
        'recent_tasks': recent_tasks,
        'stats': {
            'workspaces': len(workspaces),
            'open_tasks': open_tasks.count(),
            'my_tasks': my_open.count(),
            'due_this_week': due_this_week.count(),
            'overdue': overdue.count(),
            'time_today_label': time_today_label,
        },
        'today': today,
        **_nav_context(request.user, request=request),
    })


@login_required
@require_POST
def workspace_create(request):
    name = (request.POST.get('name') or '').strip()
    purpose = request.POST.get('purpose', '').strip().lower()
    if purpose not in {k for k, _ in Workspace.PURPOSE_CHOICES}:
        purpose = ''
    # Determine the organization to link this space to
    org_id = request.POST.get('organization_id')
    organization = None
    if org_id and str(org_id).isdigit():
        organization = _accessible_orgs(request.user).filter(pk=int(org_id)).first()
    if not organization:
        organization = _accessible_orgs(request.user).first()
    if not organization:
        # Auto-create a default org for this user
        organization = Organization.objects.create(
            name=f"{request.user.username}'s Workspace",
            owner=request.user,
        )
        request.session['active_org_id'] = organization.pk
    if name:
        ws = Workspace.objects.create(name=name, purpose=purpose, owner=request.user, organization=organization)
        # Ensure we switch the active org so the new space is visible
        request.session['active_org_id'] = organization.pk
        return redirect('workspaces:detail', workspace_id=ws.pk)
    return redirect('workspaces:list')


@login_required
@require_POST
def workspace_delete(request, workspace_id):
    ws = get_object_or_404(_accessible_workspaces(request.user), pk=workspace_id)
    ws.delete()
    return redirect('workspaces:list')


@login_required
def workspace_categories(request, workspace_id):
    import re as _re
    ws = get_object_or_404(_accessible_workspaces(request.user), pk=workspace_id)
    cats = ws.categories.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            name = (request.POST.get('name') or '').strip()
            color = request.POST.get('color', 'blue')
            if name:
                key = _re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')[:50]
                if not ws.categories.filter(key=key).exists():
                    pos = (cats.last().position + 1) if cats.exists() else 0
                    Category.objects.create(workspace=ws, key=key, name=name, color=color, position=pos)
            return redirect('workspaces:workspace_categories', workspace_id=ws.id)
        if action == 'delete':
            cat_id = request.POST.get('cat_id')
            ws.categories.filter(id=cat_id).delete()
            return redirect('workspaces:workspace_categories', workspace_id=ws.id)
        if action == 'update':
            cat_id = request.POST.get('cat_id')
            cat = ws.categories.filter(id=cat_id).first()
            if cat:
                new_name = (request.POST.get('name') or '').strip()
                new_color = request.POST.get('color', '')
                if new_name and new_name != cat.name:
                    cat.name = new_name
                    cat.key = _re.sub(r'[^a-z0-9]+', '_', new_name.lower()).strip('_')[:50]
                if new_color:
                    cat.color = new_color
                cat.save()
            return redirect('workspaces:workspace_categories', workspace_id=ws.id)
        if action == 'copy_from':
            source_ws_id = request.POST.get('source_workspace')
            if source_ws_id and source_ws_id.isdigit():
                source_ws = _accessible_workspaces(request.user).filter(pk=int(source_ws_id)).first()
                if source_ws:
                    existing_keys = set(ws.categories.values_list('key', flat=True))
                    pos = (cats.last().position + 1) if cats.exists() else 0
                    for src_cat in source_ws.categories.all():
                        if src_cat.key not in existing_keys:
                            Category.objects.create(
                                workspace=ws, key=src_cat.key, name=src_cat.name,
                                color=src_cat.color, position=pos,
                            )
                            existing_keys.add(src_cat.key)
                            pos += 1
            return redirect('workspaces:workspace_categories', workspace_id=ws.id)
        if action == 'seed_defaults':
            existing_keys = set(ws.categories.values_list('key', flat=True))
            pos = (cats.last().position + 1) if cats.exists() else 0
            for key, name, color in DEFAULT_CATEGORIES:
                if key not in existing_keys:
                    Category.objects.create(workspace=ws, key=key, name=name, color=color, position=pos)
                    pos += 1
            return redirect('workspaces:workspace_categories', workspace_id=ws.id)

    # ── Build category rows for this workspace ─────────────────
    task_counts = dict(
        Task.objects.filter(workspace=ws, category__gt='')
        .values_list('category')
        .annotate(c=Count('id'))
        .values_list('category', 'c')
    )
    cat_rows = [{'cat': c, 'count': task_counts.get(c.key, 0)} for c in cats]

    # Sidebar workspace list with category counts
    all_ws = list(_accessible_workspaces(request.user).select_related('organization')
                  .prefetch_related('categories').order_by('organization__name', 'name'))
    sidebar_workspaces = []
    for w in all_ws:
        cat_count = w.categories.count()
        sidebar_workspaces.append({
            'ws': w,
            'count': cat_count,
            'is_current': w.id == ws.id,
        })

    # Template sources (workspaces with categories, excluding current)
    template_sources = [s for s in sidebar_workspaces if s['count'] > 0 and not s['is_current']]

    # Selected category for detail pane
    sel_id = request.GET.get('cat')
    selected_cat = None
    if sel_id and sel_id.isdigit():
        selected_cat = ws.categories.filter(id=int(sel_id)).first()

    return render(request, 'workspaces/workspace_categories.html', {
        'workspace': ws,
        'cat_rows': cat_rows,
        'selected_cat': selected_cat,
        'sidebar_workspaces': sidebar_workspaces,
        'template_sources': template_sources,
        'default_categories': DEFAULT_CATEGORIES,
        'status_colors': STATUS_COLORS,
        **_nav_context(request.user, active_workspace=ws, request=request),
    })


@login_required
def workspace_detail(request, workspace_id):
    ws = get_object_or_404(_accessible_workspaces(request.user), pk=workspace_id)
    lists = list(ws.lists.all())
    recent_lists = list(ws.lists.order_by('-created_at')[:8])
    first_list = lists[0] if lists else None
    return render(request, 'workspaces/workspace_detail.html', {
        'workspace': ws,
        'status_colors': STATUS_COLORS,
        'recent_lists': recent_lists,
        'first_list': first_list,
        **_nav_context(request.user, active_workspace=ws, request=request),
    })


@login_required
@require_POST
def workspace_update(request, workspace_id):
    ws = get_object_or_404(_accessible_workspaces(request.user), pk=workspace_id)
    field = request.POST.get('field', '')
    value = request.POST.get('value', '').strip()
    if field == 'name' and value:
        ws.name = value[:120]
        icon = request.POST.get('icon', '').strip()[:8]
        ws.icon = icon
    elif field == 'purpose':
        ws.purpose = value if value in dict(Workspace.PURPOSE_CHOICES) else ''
    elif field == 'start_date':
        ws.start_date = value or None
    elif field == 'end_date':
        ws.end_date = value or None
    elif field == 'image':
        if 'image' in request.FILES:
            ws.image = request.FILES['image']
        elif request.POST.get('clear_image') == '1':
            ws.image = None
    ws.save()
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('workspaces:detail', workspace_id=ws.pk)


# Lists
@login_required
@require_POST
def list_create(request, workspace_id):
    ws = get_object_or_404(_accessible_workspaces(request.user), pk=workspace_id)
    name = (request.POST.get('name') or '').strip()
    if name:
        color = request.POST.get('color', 'blue')
        if color not in dict(STATUS_COLORS):
            color = 'blue'
        tl = TaskList.objects.create(
            workspace=ws, name=name,
            icon=(request.POST.get('icon') or '📋')[:8],
            color=color,
        )
        if request.FILES.get('image'):
            tl.image = request.FILES['image']
            tl.save()
    return redirect('workspaces:detail', workspace_id=ws.pk)


@login_required
@require_POST
def list_delete(request, list_id):
    tl = get_object_or_404(TaskList, pk=list_id, workspace__in=_accessible_workspaces(request.user))
    ws_id = tl.workspace_id
    tl.delete()
    return redirect('workspaces:detail', workspace_id=ws_id)


@login_required
@require_POST
def list_update(request, list_id):
    tl = get_object_or_404(TaskList, pk=list_id, workspace__in=_accessible_workspaces(request.user))
    name = (request.POST.get('name') or '').strip()
    color = request.POST.get('color', tl.color)
    icon = (request.POST.get('icon') or '').strip()
    if color not in dict(STATUS_COLORS):
        color = tl.color
    if name:
        tl.name = name
    tl.color = color
    if icon:
        tl.icon = icon[:8]
    if request.FILES.get('image'):
        tl.image = request.FILES['image']
    if request.POST.get('remove_image') == '1':
        if tl.image:
            tl.image.delete(save=False)
        tl.image = None
    tl.save()
    next_url = request.POST.get('next') or ''
    if next_url.startswith('/'):
        return redirect(next_url)
    return redirect('workspaces:detail', workspace_id=tl.workspace_id)


FIELD_TYPE_META = [
    {'key': 'dropdown', 'label': 'Dropdown', 'tone': 'green',  'icon': 'cf-dropdown',
     'desc': 'Single-select options — perfect for departments, categories, or any single tag.'},
    {'key': 'labels',   'label': 'Labels',   'tone': 'green',  'icon': 'cf-labels',
     'desc': 'Multi-select options for flexible tagging across tasks.'},
    {'key': 'text',     'label': 'Text',     'tone': 'blue',   'icon': 'cf-text',
     'desc': 'Add important context to any task in just one line.'},
    {'key': 'number',   'label': 'Number',   'tone': 'teal',   'icon': 'cf-number',
     'desc': 'Account for any numbers associated with a task.'},
    {'key': 'date',     'label': 'Date',     'tone': 'brown',  'icon': 'cf-date',
     'desc': 'Mark important dates beyond the task due date.'},
    {'key': 'checkbox', 'label': 'Checkbox', 'tone': 'pink',   'icon': 'cf-check',
     'desc': 'Yes / no value — great for trigger conditions.'},
    {'key': 'url',      'label': 'Website',  'tone': 'red',    'icon': 'cf-url',
     'desc': 'Link out to docs, briefs, or final assets.'},
    {'key': 'email',    'label': 'Email',    'tone': 'azure',  'icon': 'cf-email',
     'desc': 'Capture stakeholder or contact emails on a task.'},
]


def _suggested_fields(workspace):
    """Lightweight, name-aware suggestions for the Customize drawer."""
    name = (workspace.name or '').lower()
    if 'market' in name or 'design' in name or 'brand' in name:
        return [
            {'name': 'Marketing Category', 'field_type': 'dropdown', 'desc': 'Tag tasks by campaign type — Brand, Performance, Content…'},
            {'name': 'Target Audience',    'field_type': 'text',     'desc': 'Who is this work for?'},
            {'name': 'Asset Format',       'field_type': 'labels',   'desc': 'Static, video, web, social — pick any combination.'},
            {'name': 'Feedback Deadline',  'field_type': 'date',     'desc': 'Mark important review dates separate from due date.'},
        ]
    if 'food' in name or 'safety' in name or 'compli' in name:
        return [
            {'name': 'Compliance Area',    'field_type': 'dropdown', 'desc': 'HACCP, Audit, Cert, Training…'},
            {'name': 'Risk Level',         'field_type': 'dropdown', 'desc': 'Low / Medium / High / Critical.'},
            {'name': 'Inspection Date',    'field_type': 'date',     'desc': 'When was this last reviewed?'},
            {'name': 'Site URL',           'field_type': 'url',      'desc': 'Link to facility or document.'},
        ]
    return [
        {'name': 'Category',          'field_type': 'dropdown', 'desc': 'Group tasks by area or theme.'},
        {'name': 'Owner email',       'field_type': 'email',    'desc': 'Who is responsible for this work?'},
        {'name': 'Estimated cost',    'field_type': 'number',   'desc': 'Budget or projected spend.'},
        {'name': 'Reference link',    'field_type': 'url',      'desc': 'Link to a doc, sheet, or external resource.'},
    ]


def _category_choices(workspace):
    """Return (key, name) tuples for this workspace's categories."""
    return list(workspace.categories.values_list('key', 'name'))


def _task_list_context(tl, user=None):
    return {
        'workspace': tl.workspace,
        'task_list': tl,
        'columns': _columns(tl, user=user),
        'priority_choices': Task.PRIORITY_CHOICES,
        'category_choices': _category_choices(tl.workspace),
        'status_choices': _status_choices(tl),
        'status_colors': STATUS_COLORS,
        'users': User.objects.all().order_by('username'),
        'custom_fields_for_list': _custom_fields_for_list(tl),
        'custom_values_by_task': _custom_values_for_list(tl),
        'workspace_custom_fields': list(tl.workspace.custom_fields.all()),
        'field_type_meta': FIELD_TYPE_META,
        'suggested_fields': _suggested_fields(tl.workspace),
        'recurrence_freq_choices': Task.RECURRENCE_FREQ_CHOICES,
        'recurrence_trigger_choices': Task.RECURRENCE_TRIGGER_CHOICES,
        'recurrence_action_choices': Task.RECURRENCE_ACTION_CHOICES,
    }


def _custom_fields_for_list(tl):
    """Custom fields whose scope includes this list — workspace-wide if no specific lists set,
    or globally for fields flagged is_global=True (these stretch across every workspace)."""
    workspace_scope = tl.workspace.custom_fields.filter(
        Q(lists__isnull=True) | Q(lists=tl)
    )
    global_scope = CustomField.objects.filter(is_global=True).exclude(workspace=tl.workspace)
    return list(
        (workspace_scope | global_scope)
        .prefetch_related('options')
        .distinct()
        .order_by('-is_global', 'position', 'id')
    )


def _custom_values_for_list(tl):
    """{ task_id: { field_id: value_obj } } for the list."""
    out = {}
    qs = TaskCustomFieldValue.objects.filter(task__task_list=tl).select_related('option', 'field').prefetch_related('options')
    for v in qs:
        out.setdefault(v.task_id, {})[v.field_id] = v
    return out


def _view_pref(user, task_list, view):
    """Get-or-create a ViewPreference. Read-only: never persists defaults."""
    pref = ViewPreference.objects.filter(user=user, task_list=task_list, view=view).first()
    if pref:
        return pref
    # Return an unsaved instance with defaults so templates/views can read attrs.
    return ViewPreference(user=user, task_list=task_list, view=view)


def _columns_filtered(task_list, pref, user=None, status_keys=None, show_deleted=False):
    """Build columns filtered by specific status keys.

    status_keys: list of status key strings to include (empty = show all)
    show_deleted: if True, add a "Deleted" column with soft-deleted tasks
    """
    cols = []
    for s in task_list.statuses.all():
        # If specific statuses requested, skip statuses not in the list
        if status_keys and s.key not in status_keys:
            continue
        # Default behaviour: respect show_closed_tasks pref when no filter active
        if not status_keys and not pref.show_closed_tasks and s.is_done:
            continue
        tasks_qs = task_list.tasks.filter(status=s.key, deleted_at__isnull=True).prefetch_related('assignees')
        if user:
            tasks_qs = _filter_tasks_for_user(tasks_qs, user)
        tasks = list(tasks_qs)
        if not pref.show_empty_statuses and not tasks:
            continue
        cols.append({
            'status': s, 'key': s.key, 'label': s.name,
            'color': s.color, 'tasks': tasks,
        })

    if show_deleted:
        deleted_qs = task_list.tasks.filter(deleted_at__isnull=False).prefetch_related('assignees')
        if user:
            deleted_qs = _filter_tasks_for_user(deleted_qs, user)
        cols.append({
            'status': type('S', (), {'key': '_deleted', 'name': 'Deleted', 'color': 'red', 'is_done': False})(),
            'key': '_deleted', 'label': 'Deleted',
            'color': 'red', 'tasks': list(deleted_qs),
        })
    return cols


@login_required
def list_detail(request, list_id):
    tl = get_object_or_404(TaskList, pk=list_id, workspace__in=_accessible_workspaces(request.user))
    pref = _view_pref(request.user, tl, 'list')
    raw_filter = request.GET.get('filter', '')
    # Parse comma-separated status keys (e.g. "todo,in_progress" or "deleted")
    filter_keys = [k.strip() for k in raw_filter.split(',') if k.strip()] if raw_filter else []
    show_deleted = 'deleted' in filter_keys
    status_keys = [k for k in filter_keys if k != 'deleted']
    ctx = _task_list_context(tl, user=request.user)
    all_statuses = list(tl.statuses.all())
    ctx['columns'] = _columns_filtered(tl, pref, user=request.user, status_keys=status_keys, show_deleted=show_deleted)
    ctx['all_statuses'] = all_statuses
    ctx['active_filter_keys'] = filter_keys
    return render(request, 'workspaces/detail.html', {
        **ctx,
        'view': 'list',
        'view_pref': pref,
        'status_filter': 'deleted' if show_deleted and not status_keys else ('filtered' if status_keys else ''),
        **_nav_context(request.user, active_workspace=tl.workspace, active_list=tl, request=request),
    })


@login_required
def list_board(request, list_id):
    tl = get_object_or_404(TaskList, pk=list_id, workspace__in=_accessible_workspaces(request.user))
    pref = _view_pref(request.user, tl, 'board')
    ctx = _task_list_context(tl, user=request.user)
    ctx['columns'] = _columns_filtered(tl, pref, user=request.user)
    return render(request, 'workspaces/board.html', {
        **ctx,
        'view': 'board',
        'view_pref': pref,
        **_nav_context(request.user, active_workspace=tl.workspace, active_list=tl, request=request),
    })


@login_required
def list_calendar(request, list_id):
    tl = get_object_or_404(TaskList, pk=list_id, workspace__in=_accessible_workspaces(request.user))
    today = date.today()

    view_mode = request.GET.get('view_mode', 'month')
    if view_mode not in {'day', 'week', 'month'}:
        view_mode = 'month'

    # Focal date
    raw_focal = request.GET.get('d')
    focal = None
    if raw_focal:
        try:
            from datetime import datetime as _dt
            focal = _dt.strptime(raw_focal, '%Y-%m-%d').date()
        except ValueError:
            focal = None
    if focal is None:
        # Back-compat: ?year=YYYY&month=MM (month-mode anchor)
        raw_y = request.GET.get('year')
        raw_m = request.GET.get('month')
        if raw_y or raw_m:
            try:
                y = int(raw_y or today.year)
                m = int(raw_m or today.month)
                focal = date(y, m, 1)
            except (ValueError, TypeError):
                focal = today
        else:
            focal = today

    tasks = list(_filter_tasks_for_user(tl.tasks.filter(deleted_at__isnull=True), request.user))

    def _bars_in_window(wk_start, wk_end):
        bars = []
        for t in tasks:
            s, e = _task_range(t, today)
            if not s:
                continue
            if not e:
                e = s
            if e < wk_start or s > wk_end:
                continue
            bar_start = max(s, wk_start)
            bar_end = min(e, wk_end)
            cols_in_window = (wk_end - wk_start).days + 1
            bars.append({
                'task': t,
                'col_start': (bar_start - wk_start).days + 1,
                'col_end': (bar_end - wk_start).days + 2,
                '_cols': cols_in_window,
            })
        return bars

    week_rows = []
    title = ''
    day_names = []

    if view_mode == 'day':
        bars = _bars_in_window(focal, focal)
        for b in bars:
            b['col_start'], b['col_end'] = 1, 2
        lane_count = _assign_lanes(bars)
        week_rows.append({
            'days': [{'date': focal, 'in_month': True, 'is_today': focal == today}],
            'bars': bars,
            'lane_count': lane_count,
        })
        day_names = [focal.strftime('%A')]
        title = focal.strftime('%A, %B %d, %Y')
        prev_focal = focal - timedelta(days=1)
        next_focal = focal + timedelta(days=1)

    elif view_mode == 'week':
        # Sunday-start week containing focal
        wk_start = focal - timedelta(days=(focal.weekday() + 1) % 7)
        wk_end = wk_start + timedelta(days=6)
        bars = _bars_in_window(wk_start, wk_end)
        lane_count = _assign_lanes(bars)
        week_days = [wk_start + timedelta(days=i) for i in range(7)]
        week_rows.append({
            'days': [{'date': d, 'in_month': True, 'is_today': d == today} for d in week_days],
            'bars': bars,
            'lane_count': lane_count,
        })
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        title = f"{wk_start.strftime('%b %d')} – {wk_end.strftime('%b %d, %Y')}"
        prev_focal = focal - timedelta(days=7)
        next_focal = focal + timedelta(days=7)

    else:  # month
        cal_iter = _cal.Calendar(firstweekday=6)  # Sunday-first
        weeks_dates = cal_iter.monthdatescalendar(focal.year, focal.month)
        for week_days in weeks_dates:
            wk_start, wk_end = week_days[0], week_days[6]
            bars = _bars_in_window(wk_start, wk_end)
            lane_count = _assign_lanes(bars)
            week_rows.append({
                'days': [{'date': d, 'in_month': d.month == focal.month, 'is_today': d == today} for d in week_days],
                'bars': bars,
                'lane_count': lane_count,
            })
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        title = focal.strftime('%B %Y')
        first = focal.replace(day=1)
        prev_focal = (first - timedelta(days=1)).replace(day=1)
        next_focal = (first.replace(day=28) + timedelta(days=4)).replace(day=1)

    unscheduled = [t for t in tasks if not (t.start_date or t.due_date)]
    overdue = [t for t in tasks if t.due_date and t.due_date < today and t.status != 'done']

    pref = _view_pref(request.user, tl, 'calendar')
    return render(request, 'workspaces/calendar.html', {
        **_task_list_context(tl, user=request.user),
        'view': 'calendar',
        'view_pref': pref,
        'view_mode': view_mode,
        'view_mode_label': {'day': 'Day', 'week': 'Week', 'month': 'Month'}[view_mode],
        'focal': focal,
        'today_iso': today.isoformat(),
        'prev_focal_iso': prev_focal.isoformat(),
        'next_focal_iso': next_focal.isoformat(),
        'week_rows': week_rows,
        'title': title,
        'day_names': day_names,
        'is_single_column': view_mode == 'day',
        'unscheduled_count': len(unscheduled),
        'overdue_count': len(overdue),
        **_nav_context(request.user, active_workspace=tl.workspace, active_list=tl, request=request),
    })


@login_required
def list_gantt(request, list_id):
    tl = get_object_or_404(TaskList, pk=list_id, workspace__in=_accessible_workspaces(request.user))
    today = date.today()
    tasks = list(_filter_tasks_for_user(tl.tasks.filter(deleted_at__isnull=True), request.user))

    zoom = request.GET.get('zoom', 'daily')
    if zoom not in {'daily', 'weekly', 'monthly'}:
        zoom = 'daily'
    cell_w = {'daily': 40, 'weekly': 16, 'monthly': 5}[zoom]

    dated = [(t, *_task_range(t, today)) for t in tasks]
    dated = [(t, s, e) for t, s, e in dated if s]

    if dated:
        range_start = min(s for _, s, _ in dated) - timedelta(days=3)
        range_end = max((e or s) for _, s, e in dated) + timedelta(days=3)
    else:
        range_start = today - timedelta(days=7)
        range_end = today + timedelta(days=21)

    # Min visible window per zoom level so empty/sparse charts still feel alive
    min_window = {'daily': 28, 'weekly': 84, 'monthly': 365}[zoom]
    if (range_end - range_start).days < min_window:
        range_end = range_start + timedelta(days=min_window)

    total_days = (range_end - range_start).days + 1
    days = [range_start + timedelta(days=i) for i in range(total_days)]

    weeks = []
    cur = None
    for d in days:
        wk_start = d - timedelta(days=(d.weekday() + 1) % 7)  # Sunday start
        if cur is None or cur['start'] != wk_start:
            cur = {'start': wk_start, 'end': wk_start + timedelta(days=6), 'days': 0, 'label': f"W{wk_start.isocalendar().week} {wk_start.strftime('%b %d')}"}
            weeks.append(cur)
        cur['days'] += 1

    months = []
    cur = None
    for d in days:
        m_start = d.replace(day=1)
        if cur is None or cur['start'] != m_start:
            cur = {'start': m_start, 'days': 0, 'label': m_start.strftime('%b %Y')}
            months.append(cur)
        cur['days'] += 1

    now = timezone.now()
    task_ids = [t.id for t in tasks]
    totals = {}
    for entry in TimeEntry.objects.filter(task_id__in=task_ids):
        totals[entry.task_id] = totals.get(entry.task_id, 0) + entry.duration_seconds(now)

    def _fmt_duration(secs):
        if not secs:
            return ''
        h, rem = divmod(int(secs), 3600)
        m, s = divmod(rem, 60)
        if h:
            return f"{h}h {m}m" if m else f"{h}h"
        if m:
            return f"{m}m {s}s" if s else f"{m}m"
        return f"{s}s"

    rows = []
    for t, s, e in dated:
        end = e or s
        left_days = (s - range_start).days
        span_days = (end - s).days + 1
        secs = totals.get(t.id, 0)
        rows.append({
            'task': t,
            'left_days': left_days,
            'span_days': span_days,
            'tracked_seconds': secs,
            'tracked_label': _fmt_duration(secs),
        })
    # Also include undated tasks at bottom with a collapse indicator
    for t in tasks:
        if not (t.start_date or t.due_date):
            secs = totals.get(t.id, 0)
            rows.append({
                'task': t,
                'left_days': None,
                'span_days': None,
                'tracked_seconds': secs,
                'tracked_label': _fmt_duration(secs),
            })

    today_offset = (today - range_start).days if range_start <= today <= range_end else None

    pref = _view_pref(request.user, tl, 'gantt')
    return render(request, 'workspaces/gantt.html', {
        **_task_list_context(tl, user=request.user),
        'view': 'gantt',
        'zoom': zoom,
        'cell_w': cell_w,
        'days': days,
        'weeks': weeks,
        'months': months,
        'total_days': total_days,
        'rows': rows,
        'today': today,
        'today_offset': today_offset,
        'view_pref': pref,
        **_nav_context(request.user, active_workspace=tl.workspace, active_list=tl, request=request),
    })


# Tasks
@login_required
@require_POST
def task_create(request, list_id):
    tl = get_object_or_404(TaskList, pk=list_id, workspace__in=_accessible_workspaces(request.user))
    title = (request.POST.get('title') or '').strip()
    if title:
        assignee_ids = request.POST.getlist('assignees')
        try:
            est_raw = (request.POST.get('estimated_minutes') or '').strip()
            est_minutes = int(est_raw) if est_raw else None
        except ValueError:
            est_minutes = None
        category = request.POST.get('category', '')
        valid_cats = set(tl.workspace.categories.values_list('key', flat=True))
        if category and category not in valid_cats:
            category = ''
        # Recurrence fields — recurring if a valid frequency is selected
        freq = request.POST.get('recurrence_frequency', '').strip()
        recur_kwargs = {}
        if freq and freq in dict(Task.RECURRENCE_FREQ_CHOICES):
            try:
                interval = max(1, int(request.POST.get('recurrence_interval', 1)))
            except (ValueError, TypeError):
                interval = 1
            days = request.POST.getlist('recurrence_days')
            trigger = request.POST.get('recurrence_trigger', 'on_complete')
            if trigger not in dict(Task.RECURRENCE_TRIGGER_CHOICES):
                trigger = 'on_complete'
            action = request.POST.get('recurrence_action', 'create_new')
            if action not in dict(Task.RECURRENCE_ACTION_CHOICES):
                action = 'create_new'
            recur_forever = 'recur_forever' in request.POST
            recur_count = None
            if not recur_forever:
                try:
                    recur_count = max(1, int(request.POST.get('recurrence_count', 1)))
                except (ValueError, TypeError):
                    recur_count = None
            recur_kwargs = dict(
                is_recurring=True,
                recurrence_frequency=freq,
                recurrence_interval=interval,
                recurrence_days=','.join(str(d) for d in days if d.isdigit()),
                recurrence_trigger=trigger,
                recurrence_action=action,
                recur_forever=recur_forever,
                recurrence_count=recur_count,
                recurrence_status_reset=request.POST.get('recurrence_status_reset', ''),
            )

        task = Task.objects.create(
            workspace=tl.workspace,
            task_list=tl,
            title=title,
            description=request.POST.get('description', ''),
            status=request.POST.get('status', 'todo'),
            priority=request.POST.get('priority', 'normal'),
            category=category,
            start_date=request.POST.get('start_date') or None,
            due_date=request.POST.get('due_date') or None,
            estimated_minutes=est_minutes,
            created_by=request.user,
            **recur_kwargs,
        )
        if assignee_ids:
            task.assignees.set(User.objects.filter(pk__in=assignee_ids))
        _apply_inline_custom_field_values(task, request.POST)
    next_url = request.POST.get('next') or ''
    if next_url.startswith('/'):
        return redirect(next_url)
    return redirect('workspaces:list_detail', list_id=tl.pk)


def _apply_inline_custom_field_values(task, post):
    """Reads `cf_<field_id>` keys from a POST and persists TaskCustomFieldValue rows."""
    fields = task.workspace.custom_fields.all()
    for f in fields:
        key = f'cf_{f.id}'
        if key not in post:
            continue
        if f.field_type == 'dropdown':
            opt_id = post.get(key)
            if not opt_id:
                continue
            opt = CustomFieldOption.objects.filter(field=f, pk=opt_id).first()
            if opt:
                v, _ = TaskCustomFieldValue.objects.get_or_create(task=task, field=f)
                v.option = opt
                v.save()
        elif f.field_type == 'labels':
            ids = [int(x) for x in post.getlist(key) if x.isdigit()]
            if not ids:
                continue
            v, _ = TaskCustomFieldValue.objects.get_or_create(task=task, field=f)
            v.options.set(CustomFieldOption.objects.filter(field=f, pk__in=ids))
        elif f.field_type == 'checkbox':
            # Hidden 0 + checked 1 means the last value wins; we accept '1' explicitly
            v, _ = TaskCustomFieldValue.objects.get_or_create(task=task, field=f)
            v.bool_value = post.getlist(key)[-1] == '1' if post.getlist(key) else False
            v.save()
        elif f.field_type == 'number':
            raw = (post.get(key) or '').strip()
            if not raw:
                continue
            try:
                v, _ = TaskCustomFieldValue.objects.get_or_create(task=task, field=f)
                v.number_value = float(raw)
                v.save()
            except ValueError:
                pass
        elif f.field_type == 'date':
            raw = (post.get(key) or '').strip()
            if not raw:
                continue
            from datetime import datetime as _dt
            try:
                v, _ = TaskCustomFieldValue.objects.get_or_create(task=task, field=f)
                v.date_value = _dt.strptime(raw, '%Y-%m-%d').date()
                v.save()
            except ValueError:
                pass
        else:  # text / url / email
            raw = (post.get(key) or '').strip()
            if not raw:
                continue
            v, _ = TaskCustomFieldValue.objects.get_or_create(task=task, field=f)
            v.text_value = raw
            v.save()


def _handle_done_transition(task, done_by):
    """
    Called after a task is moved to a 'done' status.
    1. Notify all assignees that the task is complete.
    2. If the task is recurring with trigger=on_complete, create a new task
       or reopen the current one.
    """
    notify_task_completed(task, done_by)

    if not task.is_recurring or task.recurrence_trigger != 'on_complete':
        return

    # Honour recurrence_count (skip if exhausted)
    if not task.recur_forever and task.recurrence_count is not None:
        if task.recurrence_count <= 0:
            return
        task.recurrence_count -= 1
        task.save(update_fields=['recurrence_count'])

    if task.recurrence_action == 'reopen':
        reset_status = task.recurrence_status_reset or 'todo'
        task.status = reset_status
        task.save(update_fields=['status'])
        return

    # create_new — clone the task with shifted dates
    from datetime import timedelta as _td
    from dateutil.relativedelta import relativedelta

    freq = task.recurrence_frequency
    interval = task.recurrence_interval or 1
    delta = None
    if freq == 'daily':
        delta = _td(days=interval)
    elif freq == 'weekly':
        delta = _td(weeks=interval)
    elif freq == 'monthly':
        delta = relativedelta(months=interval)
    elif freq == 'yearly':
        delta = relativedelta(years=interval)
    elif freq == 'days_after':
        delta = _td(days=interval)

    new_start = (task.start_date + delta) if task.start_date and delta else task.start_date
    new_due = (task.due_date + delta) if task.due_date and delta else task.due_date

    reset_status = task.recurrence_status_reset or 'todo'

    new_task = Task.objects.create(
        workspace=task.workspace,
        task_list=task.task_list,
        title=task.title,
        description=task.description,
        status=reset_status,
        priority=task.priority,
        start_date=new_start,
        due_date=new_due,
        created_by=done_by,
        category=task.category,
        tags=task.tags,
        estimated_minutes=task.estimated_minutes,
        is_recurring=task.is_recurring,
        recurrence_frequency=task.recurrence_frequency,
        recurrence_interval=task.recurrence_interval,
        recurrence_days=task.recurrence_days,
        recurrence_trigger=task.recurrence_trigger,
        recurrence_action=task.recurrence_action,
        recur_forever=task.recur_forever,
        recurrence_count=task.recurrence_count,
        recurrence_status_reset=task.recurrence_status_reset,
        sync_recurrence_to_due=task.sync_recurrence_to_due,
    )
    # Copy assignees to the new task
    new_task.assignees.set(task.assignees.all())


@login_required
@require_POST
def task_update_status(request, task_id):
    task = get_object_or_404(Task, pk=task_id, workspace__in=_accessible_workspaces(request.user))
    new_status = request.POST.get('status')
    valid_keys = set(task.task_list.statuses.values_list('key', flat=True))
    if new_status in valid_keys:
        old_status = task.status
        task.status = new_status
        task.save(update_fields=['status'])
        if old_status != new_status:
            old_display = old_status.replace('_', ' ').title()
            new_display = new_status.replace('_', ' ').title()
            notify_task_updated(task, request.user, 'status', old_display, new_display)
            # If moved to a "done" status, notify assignees and handle recurrence
            is_done = task.task_list.statuses.filter(key=new_status, is_done=True).exists()
            if is_done:
                _handle_done_transition(task, request.user)
    return redirect('workspaces:list_detail', list_id=task.task_list_id)


@login_required
@require_POST
def status_create(request, list_id):
    tl = get_object_or_404(TaskList, pk=list_id, workspace__in=_accessible_workspaces(request.user))
    name = (request.POST.get('name') or '').strip()
    color = request.POST.get('color', 'gray')
    if color not in dict(STATUS_COLORS):
        color = 'gray'
    if name:
        import re
        base = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_') or 'status'
        key = base
        i = 2
        existing = set(tl.statuses.values_list('key', flat=True))
        while key in existing:
            key = f"{base}_{i}"
            i += 1
        position = (tl.statuses.order_by('-position').values_list('position', flat=True).first() or 0) + 1
        TaskStatus.objects.create(
            task_list=tl, key=key, name=name, color=color,
            position=position, is_done=False,
        )
    next_url = request.POST.get('next') or ''
    if next_url.startswith('/'):
        return redirect(next_url)
    return redirect('workspaces:list_board', list_id=tl.pk)


@login_required
@require_POST
def status_delete(request, status_id):
    s = get_object_or_404(TaskStatus, pk=status_id, task_list__workspace__in=_accessible_workspaces(request.user))
    tl = s.task_list
    # move any tasks in this status to the first remaining status with the lowest position (not this one)
    remaining = tl.statuses.exclude(pk=s.pk).order_by('position').first()
    if remaining:
        Task.objects.filter(task_list=tl, status=s.key).update(status=remaining.key)
    s.delete()
    return redirect('workspaces:list_board', list_id=tl.pk)


@login_required
@require_POST
def task_delete(request, task_id):
    task = get_object_or_404(Task, pk=task_id, workspace__in=_accessible_workspaces(request.user))
    list_id = task.task_list_id
    user = request.user
    is_manager = user.role == 'manager' or user.is_staff
    is_creator = task.created_by_id == user.pk
    is_space_owner = task.workspace.owner_id == user.pk
    if not (is_manager or is_creator or is_space_owner):
        messages.error(request, "You don't have permission to delete this task.")
        return redirect('workspaces:task_detail', task_id=task_id)
    from django.utils import timezone
    task.deleted_at = timezone.now()
    task.save(update_fields=['deleted_at'])
    messages.success(request, "Task moved to trash.")
    return redirect('workspaces:list_detail', list_id=list_id)


@login_required
@require_POST
def task_restore(request, task_id):
    task = get_object_or_404(Task, pk=task_id, workspace__in=_accessible_workspaces(request.user))
    task.deleted_at = None
    task.save(update_fields=['deleted_at'])
    messages.success(request, "Task restored.")
    return redirect('workspaces:list_detail', list_id=task.task_list_id)


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id, workspace__in=_accessible_workspaces(request.user))
    tl = task.task_list
    all_entries = list(task.time_entries.select_related('user').order_by('-started_at'))
    active_entries  = [e for e in all_entries if not e.is_deleted]
    deleted_entries = [e for e in all_entries if e.is_deleted]
    now = timezone.now()
    total_seconds = sum(e.duration_seconds(now) for e in active_entries)
    running = task.time_entries.filter(user=request.user, ended_at__isnull=True, deleted_at__isnull=True).first()
    cfields = _custom_fields_for_list(tl) if tl else []
    cvalues_map = {v.field_id: v for v in task.custom_values.select_related('option', 'field').prefetch_related('options').all()}
    cf_rows = []
    for cf in cfields:
        v = cvalues_map.get(cf.id)
        cf_rows.append({
            'field': cf,
            'value': v,
            'selected_option_ids': [o.id for o in v.options.all()] if v else [],
        })
    user = request.user
    is_manager = user.role == 'manager' or user.is_staff
    can_delete = is_manager or task.created_by_id == user.pk or task.workspace.owner_id == user.pk
    can_assign = is_manager
    day_choices = [(0, 'Mo'), (1, 'Tu'), (2, 'We'), (3, 'Th'), (4, 'Fr'), (5, 'Sa'), (6, 'Su')]
    return render(request, 'workspaces/task_detail.html', {
        **_task_list_context(tl, user=request.user),
        'task': task,
        'subtasks': task.subtasks.prefetch_related('assignees').all(),
        'comments': task.comments.select_related('author').all(),
        'time_entries': active_entries,
        'deleted_time_entries': deleted_entries,
        'total_tracked_seconds': total_seconds,
        'running_entry': running,
        'running_started_at': running.started_at.isoformat() if running else '',
        'custom_field_rows': cf_rows,
        'can_delete_task': can_delete,
        'can_assign_task': can_assign,
        'task_assignee_ids': set(task.assignees.values_list('id', flat=True)),
        'category_choices': _category_choices(tl.workspace),
        'recurrence_freq_choices': Task.RECURRENCE_FREQ_CHOICES,
        'recurrence_trigger_choices': Task.RECURRENCE_TRIGGER_CHOICES,
        'recurrence_action_choices': Task.RECURRENCE_ACTION_CHOICES,
        'day_choices': day_choices,
        **_nav_context(request.user, active_workspace=tl.workspace, active_list=tl, request=request),
    })


@login_required
@require_POST
def task_update(request, task_id):
    task = get_object_or_404(Task, pk=task_id, workspace__in=_accessible_workspaces(request.user))
    field = request.POST.get('field')
    value = request.POST.get('value', '')
    allowed = {'title', 'description', 'status', 'priority', 'start_date', 'due_date', 'assignees', 'estimated_minutes', 'category', 'recurrence'}
    if field not in allowed:
        return redirect('workspaces:task_detail', task_id=task.pk)

    if field == 'status':
        valid_keys = set(task.task_list.statuses.values_list('key', flat=True))
        if value not in valid_keys:
            return redirect('workspaces:task_detail', task_id=task.pk)
    if field == 'priority' and value not in dict(Task.PRIORITY_CHOICES):
        return redirect('workspaces:task_detail', task_id=task.pk)
    if field == 'category' and value and not task.workspace.categories.filter(key=value).exists():
        return redirect('workspaces:task_detail', task_id=task.pk)

    if field == 'recurrence':
        freq = request.POST.get('recurrence_frequency', '')
        if freq and freq in dict(Task.RECURRENCE_FREQ_CHOICES):
            task.is_recurring = True
            task.recurrence_frequency = freq
            try:
                task.recurrence_interval = max(1, int(request.POST.get('recurrence_interval', 1)))
            except (ValueError, TypeError):
                task.recurrence_interval = 1
            days = request.POST.getlist('recurrence_days')
            task.recurrence_days = ','.join(str(d) for d in days if d.isdigit())
            trigger = request.POST.get('recurrence_trigger', 'on_complete')
            task.recurrence_trigger = trigger if trigger in dict(Task.RECURRENCE_TRIGGER_CHOICES) else 'on_complete'
            action = request.POST.get('recurrence_action', 'create_new')
            task.recurrence_action = action if action in dict(Task.RECURRENCE_ACTION_CHOICES) else 'create_new'
            task.recur_forever = 'recur_forever' in request.POST
            if not task.recur_forever:
                try:
                    task.recurrence_count = max(1, int(request.POST.get('recurrence_count', 1)))
                except (ValueError, TypeError):
                    task.recurrence_count = None
            else:
                task.recurrence_count = None
            task.recurrence_status_reset = request.POST.get('recurrence_status_reset', '')
        else:
            # Remove recurring
            task.is_recurring = False
            task.recurrence_frequency = ''
        task.save()
        return redirect('workspaces:task_detail', task_id=task.pk)

    # Handle assignees separately — only notify newly-added users
    if field == 'assignees':
        old_assignee_set = set(task.assignees.all())
        new_ids = request.POST.getlist('value')
        new_users = set(User.objects.filter(pk__in=new_ids)) if new_ids else set()
        task.assignees.set(new_users)
        added = new_users - old_assignee_set
        if added:
            from .notifications import notify_assigned
            notify_assigned(task, request.user, list(added))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'ok': True})
        return redirect('workspaces:task_detail', task_id=task.pk)

    # Capture old value for notification
    if field == 'status':
        old_display = task.get_status_display() if hasattr(task, 'get_status_display') else task.status
    elif field == 'priority':
        old_display = task.get_priority_display() if task.priority else 'None'
    else:
        old_display = str(getattr(task, field, '') or '')

    if field in {'start_date', 'due_date'}:
        setattr(task, field, value or None)
        task.save()
    elif field == 'estimated_minutes':
        task.estimated_minutes = int(value) if value.isdigit() else None
        task.save()
    else:
        setattr(task, field, value)
        task.save()

    # Build new display value for notification
    if field == 'status':
        new_display = task.get_status_display() if hasattr(task, 'get_status_display') else task.status
    elif field == 'priority':
        new_display = task.get_priority_display() if task.priority else 'None'
    else:
        new_display = str(getattr(task, field, '') or '')

    if old_display != new_display:
        notify_task_updated(task, request.user, field, old_display, new_display)
        # If status changed to a "done" status, notify assignees and handle recurrence
        if field == 'status' and task.task_list:
            is_done = task.task_list.statuses.filter(key=value, is_done=True).exists()
            if is_done:
                _handle_done_transition(task, request.user)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({'ok': True})
    return redirect('workspaces:task_detail', task_id=task.pk)


@login_required
@require_POST
def subtask_create(request, task_id):
    task = get_object_or_404(Task, pk=task_id, workspace__in=_accessible_workspaces(request.user))
    title = (request.POST.get('title') or '').strip()
    if title:
        kwargs = {'task': task, 'title': title}
        status = request.POST.get('status', '').strip()
        if status and status in dict(Subtask.STATUS_CHOICES):
            kwargs['status'] = status
        priority = request.POST.get('priority', '').strip()
        if priority and priority in dict(Subtask.PRIORITY_CHOICES):
            kwargs['priority'] = priority
        category = request.POST.get('category', '').strip()
        if category and task.workspace.categories.filter(key=category).exists():
            kwargs['category'] = category
        due_date = request.POST.get('due_date', '').strip()
        if due_date:
            kwargs['due_date'] = due_date
        st = Subtask.objects.create(**kwargs)
        assignee_ids = request.POST.getlist('assignees')
        if assignee_ids:
            st.assignees.set(User.objects.filter(pk__in=assignee_ids))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            assignees = []
            for u in st.assignees.all():
                assignees.append({'id': u.pk, 'username': u.username, 'initial': u.username[:1].upper(), 'name': u.get_full_name() or u.username})
            return JsonResponse({'ok': True, 'id': st.pk, 'title': st.title, 'status': st.status, 'priority': st.priority or '', 'category': st.category or '', 'is_done': st.is_done, 'assignees': assignees})
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({'ok': False, 'error': 'Title required'}, status=400)
    return redirect('workspaces:task_detail', task_id=task.pk)


@login_required
@require_POST
def subtask_update(request, subtask_id):
    st = get_object_or_404(Subtask, pk=subtask_id, task__workspace__in=_accessible_workspaces(request.user))
    field = request.POST.get('field', '').strip()
    value = request.POST.get('value', '').strip()
    if field == 'status' and value in dict(Subtask.STATUS_CHOICES):
        st.status = value
        st.is_done = value == 'done'
        st.save(update_fields=['status', 'is_done'])
    elif field == 'priority' and (value == '' or value in dict(Subtask.PRIORITY_CHOICES)):
        st.priority = value
        st.save(update_fields=['priority'])
    elif field == 'category' and (value == '' or st.task.workspace.categories.filter(key=value).exists()):
        st.category = value
        st.save(update_fields=['category'])
    elif field == 'assignees':
        new_ids = request.POST.getlist('value')
        new_users = User.objects.filter(pk__in=new_ids) if new_ids else User.objects.none()
        st.assignees.set(new_users)
    elif field == 'due_date':
        st.due_date = value if value else None
        st.save(update_fields=['due_date'])
    elif field == 'title' and value:
        st.title = value
        st.save(update_fields=['title'])
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({'ok': True})
    return redirect('workspaces:task_detail', task_id=st.task_id)


@login_required
@require_POST
def subtask_toggle(request, subtask_id):
    st = get_object_or_404(Subtask, pk=subtask_id, task__workspace__in=_accessible_workspaces(request.user))
    st.is_done = not st.is_done
    st.status = 'done' if st.is_done else 'todo'
    st.save(update_fields=['is_done', 'status'])
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({'ok': True, 'is_done': st.is_done, 'status': st.status})
    return redirect('workspaces:task_detail', task_id=st.task_id)


@login_required
@require_POST
def subtask_delete(request, subtask_id):
    st = get_object_or_404(Subtask, pk=subtask_id, task__workspace__in=_accessible_workspaces(request.user))
    task_id = st.task_id
    st.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({'ok': True})
    return redirect('workspaces:task_detail', task_id=task_id)


@login_required
@require_POST
def comment_create(request, task_id):
    task = get_object_or_404(Task, pk=task_id, workspace__in=_accessible_workspaces(request.user))
    body = (request.POST.get('body') or '').strip()
    if body:
        comment = TaskComment.objects.create(task=task, author=request.user, body=body)
        notify_comment_added(task, comment)
    return redirect('workspaces:task_detail', task_id=task.pk)


@login_required
@require_POST
def time_start(request, task_id):
    task = get_object_or_404(Task, pk=task_id, workspace__in=_accessible_workspaces(request.user))
    # Stop any other running timer this user has (across any task)
    TimeEntry.objects.filter(user=request.user, ended_at__isnull=True).update(ended_at=timezone.now())
    TimeEntry.objects.create(task=task, user=request.user, started_at=timezone.now())
    return redirect('workspaces:task_detail', task_id=task.pk)


@login_required
@require_POST
def time_stop(request, task_id):
    task = get_object_or_404(Task, pk=task_id, workspace__in=_accessible_workspaces(request.user))
    running = TimeEntry.objects.filter(task=task, user=request.user, ended_at__isnull=True).first()
    if running:
        running.ended_at = timezone.now()
        running.save(update_fields=['ended_at'])
    return redirect('workspaces:task_detail', task_id=task.pk)


@login_required
@require_POST
def time_add(request, task_id):
    task = get_object_or_404(Task, pk=task_id, workspace__in=_accessible_workspaces(request.user))
    def _to_int(name):
        try:
            return max(0, int((request.POST.get(name) or '').strip() or 0))
        except ValueError:
            return 0
    hours = _to_int('hours')
    minutes = _to_int('minutes')
    total = hours * 60 + minutes
    if total > 0:
        now = timezone.now()
        TimeEntry.objects.create(
            task=task, user=request.user,
            started_at=now,
            ended_at=now + timezone.timedelta(minutes=total),
            is_manual=True,
        )
    return redirect('workspaces:task_detail', task_id=task.pk)


@login_required
@require_POST
def time_entry_delete(request, entry_id):
    from django.http import JsonResponse
    entry = get_object_or_404(TimeEntry, pk=entry_id, task__workspace__in=_accessible_workspaces(request.user))
    task_id = entry.task_id
    entry.deleted_at = timezone.now()
    entry.save(update_fields=['deleted_at'])
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})
    return redirect('workspaces:task_detail', task_id=task_id)


# ---------- User management (admin only) ----------

def _staff_required(view):
    from functools import wraps
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Admin access required")
        return view(request, *args, **kwargs)
    return wrapper


def _manager_or_staff_required(view):
    from functools import wraps
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        if request.user.is_staff or request.user.role == 'manager':
            return view(request, *args, **kwargs)
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Manager access required")
    return wrapper


@login_required
@_manager_or_staff_required
def user_list(request):
    users = User.objects.all().order_by('username')
    all_workspaces = Workspace.objects.select_related('organization').all().order_by('name')
    # Build user-id → list of allocated workspace memberships
    allocations = {}
    for m in WorkspaceMember.objects.select_related('workspace').all():
        allocations.setdefault(m.user_id, []).append(m)
    # Also track workspace ownership
    owned_workspaces = {}
    for ws in all_workspaces:
        owned_workspaces.setdefault(ws.owner_id, []).append(ws)
    # Group workspaces by organization for the allocation UI
    from collections import OrderedDict
    workspaces_by_org = OrderedDict()
    for ws in all_workspaces.order_by('organization__name', 'name'):
        org_name = ws.organization.name if ws.organization else 'No Organization'
        workspaces_by_org.setdefault(org_name, []).append(ws)
    # Build list data: workspace_id → [{id, name}, ...]
    all_lists = TaskList.objects.select_related('workspace').order_by('workspace_id', 'name')
    lists_by_workspace = {}
    for tl in all_lists:
        lists_by_workspace.setdefault(tl.workspace_id, []).append(tl)
    # Build user list memberships: user_id → set of list ids
    list_allocations = {}
    for lm in ListMember.objects.all():
        list_allocations.setdefault(lm.user_id, set()).add(lm.task_list_id)
    return render(request, 'workspaces/users.html', {
        'active_nav': 'users',
        'users_all': users,
        'all_workspaces': all_workspaces,
        'workspaces_by_org': workspaces_by_org,
        'allocations': allocations,
        'owned_workspaces': owned_workspaces,
        'lists_by_workspace': lists_by_workspace,
        'list_allocations': list_allocations,
        **_nav_context(request.user, request=request),
    })


@login_required
@_manager_or_staff_required
@require_POST
def user_create(request):
    import uuid
    from .models import PasswordSetupToken
    from .notifications import generate_otp, send_otp_email
    email = (request.POST.get('email') or '').strip()
    first_name = (request.POST.get('first_name') or '').strip()
    last_name = (request.POST.get('last_name') or '').strip()
    if not email:
        messages.error(request, "Email is required.")
        return redirect('workspaces:user_list')
    if User.objects.filter(email=email).exists():
        messages.error(request, "A user with this email already exists.")
        return redirect('workspaces:user_list')
    role = request.POST.get('role', 'employee')
    if role not in ('employee', 'manager'):
        role = 'employee'
    # Generate a temporary username — user will choose their own via OTP page
    temp_username = f'user_{uuid.uuid4().hex[:8]}'
    # Create user with unusable password — they'll set username + password via OTP
    u = User.objects.create_user(username=temp_username, email=email, password=None,
                                 first_name=first_name, last_name=last_name, role=role)
    u.set_unusable_password()
    u.save()
    # Allocate to selected workspaces
    ws_ids = request.POST.getlist('workspaces')
    if ws_ids:
        for ws in Workspace.objects.filter(pk__in=ws_ids):
            WorkspaceMember.objects.get_or_create(workspace=ws, user=u, defaults={'role': 'editor'})
    # Generate OTP and send email
    otp = generate_otp()
    PasswordSetupToken.objects.create(user=u, token=otp)
    send_otp_email(u, otp, is_new_user=True)
    messages.success(request, f"User created. A setup code has been sent to {email}.")
    return redirect('workspaces:user_list')


@login_required
@_staff_required
@require_POST
def user_toggle_staff(request, user_id):
    u = get_object_or_404(User, pk=user_id)
    if u.pk != request.user.pk:
        u.is_staff = not u.is_staff
        u.save(update_fields=['is_staff'])
    return redirect('workspaces:user_list')


@login_required
@_manager_or_staff_required
@require_POST
def user_set_role(request, user_id):
    u = get_object_or_404(User, pk=user_id)
    role = request.POST.get('role', 'employee')
    if role in ('employee', 'manager'):
        # Prevent self-demotion (would lock yourself out of admin)
        if u.pk == request.user.pk and role != 'manager':
            messages.error(request, "You cannot demote yourself. Ask another manager to change your role.")
            return redirect('workspaces:user_list')
        u.role = role
        u.save(update_fields=['role'])
        messages.success(request, f"Role updated for {u.username}.")
    return redirect('workspaces:user_list')


@login_required
@_manager_or_staff_required
@require_POST
def user_reset_password(request, user_id):
    u = get_object_or_404(User, pk=user_id)
    new_password = (request.POST.get('password') or '').strip()
    if new_password:
        u.set_password(new_password)
        u.save()
        messages.success(request, f"Password reset for {u.username}.")
    return redirect('workspaces:user_list')


@login_required
@_manager_or_staff_required
@require_POST
def user_send_otp(request, user_id):
    """Send a password-reset OTP to a user via email."""
    from django.http import JsonResponse
    from .models import PasswordSetupToken
    from .notifications import generate_otp, send_otp_email
    u = get_object_or_404(User, pk=user_id)
    if not u.email:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': 'User has no email address.'})
        messages.error(request, f"{u.username} has no email address.")
        return redirect('workspaces:user_list')
    # Invalidate previous unused tokens
    PasswordSetupToken.objects.filter(user=u, is_used=False).update(is_used=True)
    otp = generate_otp()
    PasswordSetupToken.objects.create(user=u, token=otp)
    send_otp_email(u, otp, is_new_user=False)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'message': f'OTP sent to {u.email}'})
    messages.success(request, f"Password reset code sent to {u.email}.")
    return redirect('workspaces:user_list')


def otp_verify(request):
    """Public page: user enters OTP code, (optionally) chooses username, and sets password."""
    from .models import PasswordSetupToken
    error = ''
    mode = request.GET.get('mode', request.POST.get('mode', 'setup'))  # 'setup' or 'reset'
    prefill_username = request.GET.get('u', request.POST.get('u', ''))

    if request.method == 'POST':
        otp_code = (request.POST.get('otp') or '').strip()
        username = (request.POST.get('username') or '').strip()
        password1 = (request.POST.get('password') or '').strip()
        password2 = (request.POST.get('password_confirm') or '').strip()

        if not all([otp_code, password1, password2]):
            error = 'All fields are required.'
        elif password1 != password2:
            error = 'Passwords do not match.'
        elif len(password1) < 6:
            error = 'Password must be at least 6 characters.'
        elif mode == 'setup' and (not username or len(username) < 3):
            error = 'Username must be at least 3 characters.'
        else:
            token = PasswordSetupToken.objects.filter(
                token=otp_code, is_used=False
            ).select_related('user').order_by('-created_at').first()

            if not token:
                error = 'Invalid or expired code.'
            elif token.is_expired():
                error = 'This code has expired. Please request a new one.'
                token.is_used = True
                token.save()
            else:
                u = token.user
                if mode == 'reset':
                    # Password reset — keep existing username
                    u.set_password(password1)
                    u.save()
                    token.is_used = True
                    token.save()
                    messages.success(request, 'Your password has been reset. You can now sign in.')
                    return redirect('login')
                else:
                    # Account setup — allow choosing username
                    if u.username != username and User.objects.filter(username=username).exists():
                        error = 'This username is already taken. Please choose another.'
                    else:
                        u.username = username
                        u.set_password(password1)
                        u.save()
                        token.is_used = True
                        token.save()
                        messages.success(request, 'Your account has been set up. You can now sign in.')
                        return redirect('login')

    return render(request, 'workspaces/otp_verify.html', {
        'error': error,
        'mode': mode,
        'prefill_username': prefill_username,
    })


@login_required
@_manager_or_staff_required
@require_POST
def user_update(request, user_id):
    u = get_object_or_404(User, pk=user_id)
    u.first_name = (request.POST.get('first_name') or '').strip()
    u.last_name = (request.POST.get('last_name') or '').strip()
    email = (request.POST.get('email') or '').strip()
    if email and (email == u.email or not User.objects.filter(email=email).exclude(pk=u.pk).exists()):
        u.email = email
    u.phone_number = (request.POST.get('phone_number') or '').strip()
    u.company_name = (request.POST.get('company_name') or '').strip()
    u.position = (request.POST.get('position') or '').strip()
    role = request.POST.get('role', u.role)
    if role in ('employee', 'manager'):
        # Prevent self-demotion
        if u.pk == request.user.pk and role != 'manager':
            messages.error(request, "You cannot demote yourself. Ask another manager to change your role.")
            return redirect('workspaces:user_list')
        u.role = role
    u.is_staff = request.POST.get('is_staff') == '1'
    u.save()
    messages.success(request, f"User {u.username} updated.")
    return redirect('workspaces:user_list')


@login_required
@_manager_or_staff_required
@require_POST
def user_delete(request, user_id):
    u = get_object_or_404(User, pk=user_id)
    if u.pk == request.user.pk:
        messages.error(request, "You can't delete yourself.")
    else:
        u.delete()
    return redirect('workspaces:user_list')


@login_required
@_manager_or_staff_required
@require_POST
def user_allocate_workspace(request, user_id):
    """Add or remove a workspace allocation for a user from the Users admin page."""
    from django.http import JsonResponse
    target_user = get_object_or_404(User, pk=user_id)
    ws_id = request.POST.get('workspace_id')
    action = request.POST.get('action', 'add')
    ws = get_object_or_404(Workspace, pk=ws_id)
    if action == 'add':
        WorkspaceMember.objects.get_or_create(workspace=ws, user=target_user, defaults={'role': 'editor'})
    elif action == 'remove':
        WorkspaceMember.objects.filter(workspace=ws, user=target_user).delete()
        # Also remove list memberships for lists in this workspace
        ListMember.objects.filter(user=target_user, task_list__workspace=ws).delete()
    # Return JSON for AJAX requests
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        return JsonResponse({'ok': True, **_user_alloc_json(target_user)})
    return redirect('workspaces:user_list')


@login_required
@_manager_or_staff_required
@require_POST
def user_allocate_list(request, user_id):
    """Add or remove a list allocation for a user."""
    from django.http import JsonResponse
    target_user = get_object_or_404(User, pk=user_id)
    list_id = request.POST.get('list_id')
    action = request.POST.get('action', 'add')
    tl = get_object_or_404(TaskList, pk=list_id)
    if action == 'add':
        ListMember.objects.get_or_create(task_list=tl, user=target_user)
    elif action == 'remove':
        ListMember.objects.filter(task_list=tl, user=target_user).delete()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        return JsonResponse({'ok': True, **_user_alloc_json(target_user)})
    return redirect('workspaces:user_list')


def _user_alloc_json(user):
    """Build allocation JSON for a user (workspaces + lists)."""
    memberships = WorkspaceMember.objects.filter(user=user).select_related('workspace')
    member_list = [{'id': m.workspace.id, 'name': m.workspace.name} for m in memberships]
    owned_list = [{'id': w.id, 'name': w.name} for w in Workspace.objects.filter(owner=user)]
    list_ids = list(ListMember.objects.filter(user=user).values_list('task_list_id', flat=True))
    return {'owned': owned_list, 'member': member_list, 'list_ids': list_ids}


@login_required
def settings_page(request):
    if request.method == 'POST':
        theme = (request.POST.get('theme') or '').strip().lower()
        if theme in {'system', 'light', 'dark'}:
            request.user.theme = theme
            request.user.save(update_fields=['theme'])
        return redirect('workspaces:settings')
    return render(request, 'workspaces/settings.html', {
        'active_nav': 'settings',
        **_nav_context(request.user, request=request),
    })


# Custom Fields
DEFAULT_OPTION_COLORS = ['purple', 'pink', 'blue', 'green', 'orange', 'red', 'yellow', 'gray']


@login_required
def custom_field_manager(request, workspace_id, field_id=None):
    ws = _get_workspace_for_user(request.user, workspace_id)

    # Handle import fields from another workspace (single or multiple)
    if request.method == 'POST' and request.POST.get('action') in ('import_field', 'import_fields'):
        field_ids = request.POST.getlist('field_ids') or []
        # Also support single field_id for backwards compat
        single = request.POST.get('field_id')
        if single and single.isdigit():
            field_ids.append(single)
        valid_ids = [int(fid) for fid in field_ids if fid.isdigit()]
        if valid_ids:
            src_fields = CustomField.objects.filter(pk__in=valid_ids).prefetch_related('options')
            pos = (ws.custom_fields.order_by('-position').first().position + 1) if ws.custom_fields.exists() else 0
            for src_field in src_fields:
                new_field = CustomField.objects.create(
                    workspace=ws, name=src_field.name,
                    field_type=src_field.field_type,
                    position=pos, creator=request.user,
                )
                for opt in src_field.options.all():
                    CustomFieldOption.objects.create(
                        field=new_field, name=opt.name,
                        color=opt.color, position=opt.position,
                    )
                pos += 1
        return redirect('workspaces:custom_field_manager', workspace_id=ws.pk)

    fields = list(ws.custom_fields.prefetch_related('options', 'lists').all())
    selected_id = field_id or request.GET.get('field')
    selected = None
    if selected_id:
        selected = next((f for f in fields if str(f.id) == str(selected_id)), None)
    if selected is None and fields:
        selected = fields[0]

    # Build import sources — other workspaces' individual fields
    all_ws = list(_accessible_workspaces(request.user).prefetch_related('custom_fields__options')
                  .select_related('organization').order_by('organization__name', 'name'))
    import_sources = []
    for w in all_ws:
        if w.id == ws.id:
            continue
        ws_fields = list(w.custom_fields.all())
        if ws_fields:
            import_sources.append({'ws': w, 'fields': ws_fields})

    return render(request, 'workspaces/custom_field_manager.html', {
        'workspace': ws,
        'fields': fields,
        'selected': selected,
        'field_types': CUSTOM_FIELD_TYPES,
        'workspace_lists': list(ws.lists.all()),
        'option_colors': DEFAULT_OPTION_COLORS,
        'import_sources': import_sources,
        **_nav_context(request.user, active_workspace=ws, request=request),
    })


@login_required
@require_POST
def custom_field_create(request, workspace_id):
    ws = _get_workspace_for_user(request.user, workspace_id, require_edit=True)
    name = (request.POST.get('name') or '').strip()
    field_type = request.POST.get('field_type') or 'dropdown'
    if not name:
        return redirect('workspaces:custom_field_manager', workspace_id=ws.pk)
    valid_types = {k for k, _ in CUSTOM_FIELD_TYPES}
    if field_type not in valid_types:
        field_type = 'dropdown'
    last = ws.custom_fields.order_by('-position').first()
    pos = (last.position + 1) if last else 0
    f = CustomField.objects.create(
        workspace=ws, name=name, field_type=field_type,
        position=pos, creator=request.user,
    )
    if field_type in ('dropdown', 'labels'):
        for i, label in enumerate(['Option 1', 'Option 2', 'Option 3']):
            CustomFieldOption.objects.create(
                field=f, name=label, color=DEFAULT_OPTION_COLORS[i % len(DEFAULT_OPTION_COLORS)],
                position=i,
            )
    return redirect('workspaces:custom_field_manager_with_field', workspace_id=ws.pk, field_id=f.pk)


@login_required
@require_POST
def custom_field_quick_create(request, workspace_id):
    """Create a field with just a name + type, then return to the calling URL.
    Used by the inline panel inside the Customize drawer."""
    ws = _get_workspace_for_user(request.user, workspace_id, require_edit=True)
    name = (request.POST.get('name') or '').strip()
    field_type = request.POST.get('field_type') or 'dropdown'
    valid_types = {k for k, _ in CUSTOM_FIELD_TYPES}
    if field_type not in valid_types:
        field_type = 'dropdown'
    if not name:
        # Fall back to the type label, e.g. "Dropdown" — user can rename later
        name = dict(CUSTOM_FIELD_TYPES).get(field_type, 'Field')
    last = ws.custom_fields.order_by('-position').first()
    pos = (last.position + 1) if last else 0
    f = CustomField.objects.create(
        workspace=ws, name=name, field_type=field_type,
        position=pos, creator=request.user,
    )
    if field_type in ('dropdown', 'labels'):
        for i, label in enumerate(['Option 1', 'Option 2', 'Option 3']):
            CustomFieldOption.objects.create(
                field=f, name=label,
                color=DEFAULT_OPTION_COLORS[i % len(DEFAULT_OPTION_COLORS)],
                position=i,
            )
    next_url = request.POST.get('next') or ''
    if next_url:
        # Append a small confirmation flag so the next page can show a toast + reopen drawer
        sep = '&' if ('?' in next_url) else '?'
        return redirect(f"{next_url}{sep}cf_created={f.id}")
    return redirect('workspaces:custom_field_manager_with_field',
                    workspace_id=ws.pk, field_id=f.pk)


@login_required
@require_POST
def custom_field_update(request, field_id):
    f = get_object_or_404(CustomField, pk=field_id, workspace__in=_accessible_workspaces(request.user))
    _get_workspace_for_user(request.user, f.workspace_id, require_edit=True)
    name = (request.POST.get('name') or '').strip()
    if name:
        f.name = name
    if 'visible_to_guests' in request.POST:
        f.visible_to_guests = request.POST.get('visible_to_guests') == '1'
    if 'is_private' in request.POST:
        f.is_private = request.POST.get('is_private') == '1'
    if 'is_global' in request.POST:
        f.is_global = request.POST.get('is_global') == '1'
    if 'field_type' in request.POST:
        ft = request.POST.get('field_type')
        if ft in {k for k, _ in CUSTOM_FIELD_TYPES}:
            f.field_type = ft
    f.save()
    if 'lists' in request.POST:
        ids = [int(x) for x in request.POST.getlist('lists') if x.isdigit()]
        f.lists.set(TaskList.objects.filter(workspace=f.workspace, pk__in=ids))
    return redirect('workspaces:custom_field_manager_with_field', workspace_id=f.workspace_id, field_id=f.pk)


@login_required
@require_POST
def custom_field_delete(request, field_id):
    f = get_object_or_404(CustomField, pk=field_id, workspace__in=_accessible_workspaces(request.user))
    _get_workspace_for_user(request.user, f.workspace_id, require_edit=True)
    workspace_id = f.workspace_id
    f.delete()
    return redirect('workspaces:custom_field_manager', workspace_id=workspace_id)


@login_required
@require_POST
def custom_field_option_create(request, field_id):
    f = get_object_or_404(CustomField, pk=field_id, workspace__in=_accessible_workspaces(request.user))
    _get_workspace_for_user(request.user, f.workspace_id, require_edit=True)
    name = (request.POST.get('name') or '').strip() or 'New option'
    color = request.POST.get('color') or DEFAULT_OPTION_COLORS[0]
    last = f.options.order_by('-position').first()
    pos = (last.position + 1) if last else 0
    CustomFieldOption.objects.create(field=f, name=name, color=color, position=pos)
    return redirect('workspaces:custom_field_manager_with_field', workspace_id=f.workspace_id, field_id=f.id)


@login_required
@require_POST
def custom_field_option_update(request, option_id):
    opt = get_object_or_404(CustomFieldOption, pk=option_id, field__workspace__in=_accessible_workspaces(request.user))
    _get_workspace_for_user(request.user, opt.field.workspace_id, require_edit=True)
    name = (request.POST.get('name') or '').strip()
    color = request.POST.get('color')
    if name:
        opt.name = name
    if color:
        opt.color = color
    opt.save()
    return redirect('workspaces:custom_field_manager_with_field', workspace_id=opt.field.workspace_id, field_id=opt.field_id)


@login_required
@require_POST
def custom_field_option_delete(request, option_id):
    opt = get_object_or_404(CustomFieldOption, pk=option_id, field__workspace__in=_accessible_workspaces(request.user))
    _get_workspace_for_user(request.user, opt.field.workspace_id, require_edit=True)
    field_id = opt.field_id
    workspace_id = opt.field.workspace_id
    opt.delete()
    return redirect('workspaces:custom_field_manager_with_field', workspace_id=workspace_id, field_id=field_id)


# ---------- Organization (grand Workspace) ----------

@login_required
@require_POST
def organization_create(request):
    name = (request.POST.get('name') or '').strip()
    if name:
        org = Organization.objects.create(name=name, owner=request.user)
        request.session['active_org_id'] = org.pk
    return redirect('workspaces:list')


@login_required
def organization_switch(request, org_id):
    org = _accessible_orgs(request.user).filter(pk=org_id).first()
    if org:
        request.session['active_org_id'] = org.pk
    return redirect('workspaces:list')


# ── Dashboard card catalog ──────────────────────────────────────────────────
CARD_CATALOG = {
    # Statuses
    'status_breakdown_pie':  {'label': 'Workload by Status',   'desc': 'Pie chart of statuses usage',             'category': 'Statuses',       'default_width': 'half'},
    'status_breakdown_bar':  {'label': 'Status Breakdown',     'desc': 'Bar chart of statuses',                   'category': 'Statuses',       'default_width': 'half'},
    'tasks_in_progress':     {'label': 'Tasks In Progress',    'desc': 'Count of in-progress tasks',              'category': 'Statuses',       'default_width': 'half'},
    'tasks_completed':       {'label': 'Tasks Completed',      'desc': 'Count of completed tasks',                'category': 'Statuses',       'default_width': 'half'},
    # Assignees
    'tasks_by_assignee_pie': {'label': 'Tasks by Assignee',    'desc': 'Pie chart of tasks per assignee',         'category': 'Assignees',      'default_width': 'half'},
    'tasks_by_assignee_bar': {'label': 'Tasks by Assignee',    'desc': 'Bar chart of tasks per assignee',         'category': 'Assignees',      'default_width': 'half'},
    'unassigned_tasks':      {'label': 'Unassigned Tasks',     'desc': 'Count of tasks with no assignee',         'category': 'Assignees',      'default_width': 'half'},
    # Priorities
    'priority_breakdown_pie':{'label': 'Priority Breakdown',   'desc': 'Pie chart by priority',                   'category': 'Priorities',     'default_width': 'half'},
    'priority_breakdown_bar':{'label': 'Priority Breakdown',   'desc': 'Bar chart by priority',                   'category': 'Priorities',     'default_width': 'half'},
    'urgent_tasks':          {'label': 'Urgent Tasks',         'desc': 'Count of urgent-priority tasks',          'category': 'Priorities',     'default_width': 'half'},
    # Time Tracking
    'time_logged':           {'label': 'Time Logged',          'desc': 'Total time tracked',                      'category': 'Time Tracking',  'default_width': 'half'},
    'time_by_category':      {'label': 'Hours by Category',    'desc': 'Time grouped by task category',           'category': 'Time Tracking',  'default_width': 'half'},
    'time_by_workspace':     {'label': 'Hours per Company',    'desc': 'Time tracked by workspace',               'category': 'Time Tracking',  'default_width': 'half'},
    # Tables
    'overdue_tasks':         {'label': 'Overdue Tasks',        'desc': 'List of overdue tasks',                   'category': 'Tables',         'default_width': 'full'},
    'tasks_due_soon':        {'label': 'Tasks Due Soon',       'desc': 'Tasks due in the next 14 days',           'category': 'Tables',         'default_width': 'full'},
    'team_performance':      {'label': 'Team Performance',     'desc': 'Team workload and completion rates',       'category': 'Tables',         'default_width': 'full'},
    'task_list_table':       {'label': 'Task List',            'desc': 'Recent tasks table',                      'category': 'Tables',         'default_width': 'full'},
    # Charts
    'activity_trend':        {'label': 'Activity Trend',       'desc': 'Created vs completed over time',          'category': 'Charts',         'default_width': 'full'},
    'progress':              {'label': 'Overall Progress',     'desc': 'Completion percentage with progress bar', 'category': 'Charts',         'default_width': 'half'},
    'velocity':              {'label': 'Velocity',             'desc': 'Tasks completed per week',                'category': 'Charts',         'default_width': 'half'},
    'cycle_time':            {'label': 'Cycle Time',           'desc': 'Average days to completion',              'category': 'Charts',         'default_width': 'half'},
    # Task Breakdowns
    'total_tasks_kpi':       {'label': 'Total Tasks',          'desc': 'Count of all tasks',                      'category': 'Task Breakdowns', 'default_width': 'half'},
    'completion_rate_kpi':   {'label': 'Completion Rate',      'desc': 'Percentage of tasks completed',           'category': 'Task Breakdowns', 'default_width': 'half'},
    'overdue_pct_kpi':       {'label': 'Overdue Rate',         'desc': 'Percentage of tasks overdue',             'category': 'Task Breakdowns', 'default_width': 'half'},
    'tasks_no_due_date':     {'label': 'No Due Date',          'desc': 'Tasks with no due date set',              'category': 'Task Breakdowns', 'default_width': 'half'},
    'tasks_due_this_week':   {'label': 'Due This Week',        'desc': 'Tasks due in the current week',           'category': 'Task Breakdowns', 'default_width': 'half'},
    'tasks_by_workspace_pie':{'label': 'Tasks by Space',       'desc': 'Pie chart of tasks per workspace',        'category': 'Task Breakdowns', 'default_width': 'half'},
    'tasks_by_workspace_bar':{'label': 'Tasks by Space',       'desc': 'Bar chart of tasks per workspace',        'category': 'Task Breakdowns', 'default_width': 'half'},
    'tasks_by_list_bar':     {'label': 'Tasks by List',        'desc': 'Bar chart of tasks per list',             'category': 'Task Breakdowns', 'default_width': 'half'},
    'tasks_by_category_pie': {'label': 'Tasks by Category',    'desc': 'Pie chart of tasks by category',          'category': 'Task Breakdowns', 'default_width': 'half'},
    # Subtask KPIs
    'subtask_progress':      {'label': 'Subtask Progress',     'desc': 'Subtask completion percentage',           'category': 'Subtask KPIs',   'default_width': 'half'},
    'subtask_total':         {'label': 'Total Subtasks',       'desc': 'Count of all subtasks',                   'category': 'Subtask KPIs',   'default_width': 'half'},
    'subtask_overdue':       {'label': 'Overdue Subtasks',     'desc': 'Subtasks past their due date',            'category': 'Subtask KPIs',   'default_width': 'half'},
    'subtask_unassigned':    {'label': 'Unassigned Subtasks',  'desc': 'Subtasks with no assignee',               'category': 'Subtask KPIs',   'default_width': 'half'},
    'subtask_no_due_date':   {'label': 'No Due Date',          'desc': 'Subtasks with no due date set',           'category': 'Subtask KPIs',   'default_width': 'half'},
    'subtask_due_soon':      {'label': 'Due Soon',             'desc': 'Subtasks due in the next 14 days',        'category': 'Subtask KPIs',   'default_width': 'half'},
    # Subtask Charts
    'subtask_status_pie':    {'label': 'Subtask Status',       'desc': 'Pie chart of subtask statuses',           'category': 'Subtask Charts',  'default_width': 'half'},
    'subtask_status_bar':    {'label': 'Subtask Status',       'desc': 'Bar chart of subtask statuses',           'category': 'Subtask Charts',  'default_width': 'half'},
    'subtask_priority_pie':  {'label': 'Subtask Priority',     'desc': 'Pie chart of subtask priorities',         'category': 'Subtask Charts',  'default_width': 'half'},
    'subtask_priority_bar':  {'label': 'Subtask Priority',     'desc': 'Bar chart of subtask priorities',         'category': 'Subtask Charts',  'default_width': 'half'},
    'subtask_by_assignee':   {'label': 'Subtasks by Assignee', 'desc': 'Bar chart of subtasks per person',        'category': 'Subtask Charts',  'default_width': 'half'},
    'subtask_assignee_pie':  {'label': 'Subtasks by Assignee', 'desc': 'Pie chart of subtasks per person',        'category': 'Subtask Charts',  'default_width': 'half'},
    'subtask_by_workspace':  {'label': 'Subtasks by Space',    'desc': 'Bar chart of subtasks per workspace',     'category': 'Subtask Charts',  'default_width': 'half'},
    'subtask_by_list':       {'label': 'Subtasks by List',     'desc': 'Bar chart of subtasks per list',          'category': 'Subtask Charts',  'default_width': 'half'},
    'subtask_by_parent':     {'label': 'By Parent Status',     'desc': 'Subtasks grouped by parent task status',  'category': 'Subtask Charts',  'default_width': 'half'},
    'subtask_by_category':   {'label': 'Subtasks by Category', 'desc': 'Bar chart of subtasks by category',       'category': 'Subtask Charts',  'default_width': 'half'},
    'subtask_done_vs_open':  {'label': 'Done vs Open',         'desc': 'Subtask completion split',                'category': 'Subtask Charts',  'default_width': 'half'},
    # Subtask Tables
    'subtask_overdue_table': {'label': 'Overdue Subtasks',     'desc': 'Table of overdue subtasks',               'category': 'Subtask Tables',  'default_width': 'full'},
    'subtask_due_soon_table':{'label': 'Subtasks Due Soon',    'desc': 'Subtasks due in the next 14 days',        'category': 'Subtask Tables',  'default_width': 'full'},
    'subtask_table':         {'label': 'Recent Subtasks',      'desc': 'Latest subtasks table',                   'category': 'Subtask Tables',  'default_width': 'full'},
}

# Category display order for the catalog drawer
CARD_CATALOG_ORDER = ['Statuses', 'Assignees', 'Priorities', 'Task Breakdowns', 'Subtask KPIs', 'Subtask Charts', 'Subtask Tables', 'Time Tracking', 'Tables', 'Charts']


def _card_catalog_grouped():
    from collections import OrderedDict
    groups = OrderedDict()
    for cat in CARD_CATALOG_ORDER:
        groups[cat] = []
    for key, meta in CARD_CATALOG.items():
        cat = meta['category']
        groups.setdefault(cat, []).append({'key': key, **meta})
    return groups


def _fmt_dur(s):
    if not s:
        return '\u2014'
    h, rem = divmod(int(s), 3600)
    m = rem // 60
    if h:
        return f"{h}h {m:02d}m"
    if m:
        return f"{m}m"
    return f"{rem}s"


def _compute_dashboard_data(request):
    """Compute all metrics for dashboard cards. Returns a context dict."""
    import json as _json

    active_org = _active_org(request)
    workspaces = list(_accessible_workspaces(request.user, organization=active_org))
    today = date.today()
    now_dt = timezone.now()

    # ── Drill-down scope (supports multi-select) ────────────────────────────
    ws_id_strs = request.GET.getlist('workspace')
    list_id_strs = request.GET.getlist('list')
    ws_ids = [int(x) for x in ws_id_strs if x.isdigit()]
    list_ids = [int(x) for x in list_id_strs if x.isdigit()]

    selected_workspaces = [w for w in workspaces if w.id in ws_ids] if ws_ids else []
    selected_ws = selected_workspaces[0] if len(selected_workspaces) == 1 else None  # compat
    lists_in_ws = []
    if selected_workspaces:
        lists_in_ws = list(TaskList.objects.filter(workspace__in=selected_workspaces).order_by('name'))
    selected_lists = [l for l in lists_in_ws if l.id in list_ids] if list_ids else []
    selected_list = selected_lists[0] if len(selected_lists) == 1 else None  # compat

    if selected_lists:
        base_qs = Task.objects.filter(task_list__in=selected_lists, deleted_at__isnull=True)
    elif selected_workspaces:
        base_qs = Task.objects.filter(workspace__in=selected_workspaces, deleted_at__isnull=True)
    else:
        base_qs = Task.objects.filter(workspace__in=workspaces, deleted_at__isnull=True)

    selected_ws_ids = set(ws_ids)
    selected_list_ids = set(list_ids)

    # ── Period ────────────────────────────────────────────────────────────────
    period = request.GET.get('period', 'monthly')
    period_days_map = {'daily': 1, 'weekly': 7, 'monthly': 30, 'quarter': 90, 'all': None}
    if period not in period_days_map:
        period = 'monthly'
    period_days = period_days_map[period]

    if period_days is not None:
        period_start = today - timedelta(days=period_days)
        period_qs = base_qs.filter(created_at__date__gte=period_start)
    else:
        period_start = None
        period_qs = base_qs

    # ── Snapshot metrics (use period_qs so period filter actually works) ─────
    qs = period_qs   # the period-filtered queryset
    total_tasks = qs.count()
    closed_tasks = qs.filter(status='done').count()
    open_tasks = total_tasks - closed_tasks
    completion_rate = round((closed_tasks / total_tasks) * 100) if total_tasks else 0
    overdue = qs.exclude(status='done').filter(due_date__lt=today).count()
    overdue_pct = round((overdue / open_tasks) * 100) if open_tasks else 0
    due_this_week = qs.exclude(status='done').filter(
        due_date__gte=today, due_date__lte=today + timedelta(days=7)).count()
    unassigned_count = qs.exclude(status='done').filter(assignees__isnull=True).count()
    no_due_date_count = qs.exclude(status='done').filter(due_date__isnull=True).count()
    in_progress_count = qs.filter(status='in_progress').count()
    urgent_count = qs.filter(priority='urgent').count()

    # Avg cycle time
    avg_cycle_days = None
    done_sample = list(qs.filter(status='done').only('created_at')[:500])
    if done_sample:
        ages = [(now_dt.date() - t.created_at.date()).days for t in done_sample]
        avg_cycle_days = round(sum(ages) / len(ages))

    # Velocity
    period_done = qs.filter(status='done').count()
    if period_days and period_days > 0:
        velocity = round(period_done / period_days * 7, 1)
    else:
        oldest = qs.order_by('created_at').values_list('created_at', flat=True).first()
        span = max((today - oldest.date()).days, 1) if oldest else 1
        velocity = round(closed_tasks / span * 7, 1)

    # ── Time tracking (also filtered by period) ───────────────────────────────
    time_qs = TimeEntry.objects.filter(task__in=base_qs, deleted_at__isnull=True)
    if period_days is not None:
        time_qs = time_qs.filter(started_at__date__gte=period_start)
    total_seconds = sum(e.duration_seconds(now_dt) for e in time_qs)

    # ── Status breakdown ──────────────────────────────────────────────────────
    statuses_list = []
    for k, label in Task.STATUS_CHOICES:
        cnt = qs.filter(status=k).count()
        statuses_list.append({
            'key': k, 'label': label, 'count': cnt,
            'pct': round((cnt / total_tasks) * 100) if total_tasks else 0,
        })

    # ── Priority breakdown ────────────────────────────────────────────────────
    priority_list = []
    max_p = 0
    for k, label in Task.PRIORITY_CHOICES:
        cnt = qs.filter(priority=k).count()
        priority_list.append({'key': k, 'label': label, 'count': cnt})
        max_p = max(max_p, cnt)
    for p in priority_list:
        p['pct'] = round((p['count'] / max_p) * 100) if max_p else 0

    # ── Team table ────────────────────────────────────────────────────────────
    team_map = {}
    for t in qs.filter(assignees__isnull=False).prefetch_related('assignees').distinct():
        for u in t.assignees.all():
            r = team_map.setdefault(u.id, {
                'name': u.get_full_name() or u.username,
                'open': 0, 'done': 0, 'overdue': 0, 'seconds': 0,
            })
            if t.status == 'done':
                r['done'] += 1
            else:
                r['open'] += 1
                if t.due_date and t.due_date < today:
                    r['overdue'] += 1
    for entry in time_qs.select_related('user'):
        u = entry.user
        secs = entry.duration_seconds(now_dt)
        if u.id in team_map:
            team_map[u.id]['seconds'] += secs
        else:
            team_map[u.id] = {
                'name': u.get_full_name() or u.username,
                'open': 0, 'done': 0, 'overdue': 0, 'seconds': secs,
            }
    for r in team_map.values():
        r['total'] = r['open'] + r['done']
        r['time_label'] = _fmt_dur(r['seconds'])
        r['done_pct'] = round((r['done'] / r['total']) * 100) if r['total'] else 0
    team_rows = sorted(team_map.values(), key=lambda r: -r['total'])[:15]

    # Assignee breakdown for pie/bar charts
    assignee_rows = []
    for r in team_rows:
        assignee_rows.append({'name': r['name'], 'count': r['total']})

    # ── Hours by category ─────────────────────────────────────────────────────
    category_hours = {}
    for entry in time_qs.select_related('task'):
        cat = entry.task.category or 'uncategorized'
        category_hours[cat] = category_hours.get(cat, 0) + entry.duration_seconds(now_dt)
    category_rows = []
    cat_labels = dict(Category.objects.filter(
        workspace__in=_accessible_workspaces(request.user)
    ).values_list('key', 'name'))
    cat_labels['uncategorized'] = 'Uncategorized'
    for cat_key, secs in sorted(category_hours.items(), key=lambda x: -x[1]):
        category_rows.append({
            'key': cat_key,
            'label': cat_labels.get(cat_key, cat_key.title()),
            'seconds': secs,
            'hours': round(secs / 3600, 1),
            'time_label': _fmt_dur(secs),
            'pct': round((secs / total_seconds) * 100) if total_seconds else 0,
        })

    # ── Hours per workspace ───────────────────────────────────────────────────
    workspace_hours = {}
    for entry in time_qs.select_related('task__workspace'):
        ws = entry.task.workspace
        workspace_hours.setdefault(ws.id, {'name': ws.name, 'seconds': 0})
        workspace_hours[ws.id]['seconds'] += entry.duration_seconds(now_dt)
    workspace_hour_rows = sorted(workspace_hours.values(), key=lambda r: -r['seconds'])
    for r in workspace_hour_rows:
        r['hours'] = round(r['seconds'] / 3600, 1)
        r['time_label'] = _fmt_dur(r['seconds'])
        r['pct'] = round((r['seconds'] / total_seconds) * 100) if total_seconds else 0

    # ── Activity trend ────────────────────────────────────────────────────────
    if period == 'all':
        earliest = (base_qs.order_by('created_at')
                    .values_list('created_at__date', flat=True).first())
        trend_start = earliest if earliest else (today - timedelta(days=27))
    else:
        trend_days_map2 = {'daily': 14, 'weekly': 14, 'monthly': 28, 'quarter': 90}
        trend_start = today - timedelta(days=trend_days_map2.get(period, 28) - 1)

    created_by_day = dict(
        base_qs.annotate(day=TruncDate('created_at'))
        .values('day').annotate(n=Count('id')).values_list('day', 'n')
    )
    done_by_day = dict(
        base_qs.filter(status='done')
        .annotate(day=TruncDate('created_at'))
        .values('day').annotate(n=Count('id')).values_list('day', 'n')
    )
    chart_labels, chart_created, chart_done_data = [], [], []
    d = trend_start
    while d <= today:
        chart_labels.append(d.strftime('%b %d'))
        chart_created.append(created_by_day.get(d, 0))
        chart_done_data.append(done_by_day.get(d, 0))
        d += timedelta(days=1)

    # ── Overdue detail ────────────────────────────────────────────────────────
    overdue_tasks_qs = (qs.exclude(status='done')
                        .filter(due_date__lt=today)
                        .select_related('workspace', 'task_list').prefetch_related('assignees')
                        .order_by('due_date')[:15])

    # ── Due-soon detail ───────────────────────────────────────────────────────
    due_soon_tasks_qs = (qs.exclude(status='done')
                         .filter(due_date__gte=today, due_date__lte=today + timedelta(days=14))
                         .select_related('workspace', 'task_list').prefetch_related('assignees')
                         .order_by('due_date')[:20])

    # ── Recent tasks ──────────────────────────────────────────────────────────
    recent_tasks_qs = (qs
                       .select_related('workspace', 'task_list').prefetch_related('assignees')
                       .order_by('-created_at')[:20])

    # ── Activity trend preview (for catalog tile) ───────────────────────────
    # Aggregate into 4 buckets for the mini bar preview
    trend_preview = []
    if chart_created:
        n = len(chart_created)
        bucket_size = max(1, n // 4)
        for i in range(4):
            start = i * bucket_size
            end = start + bucket_size if i < 3 else n
            c_sum = sum(chart_created[start:end])
            d_sum = sum(chart_done_data[start:end])
            trend_preview.append({'created': c_sum, 'done': d_sum})
        trend_max = max(max(b['created'] for b in trend_preview), max(b['done'] for b in trend_preview), 1)
        for b in trend_preview:
            b['created_pct'] = round((b['created'] / trend_max) * 100)
            b['done_pct'] = round((b['done'] / trend_max) * 100)

    # ── Preview arc helper (must be before usage) ──────────────────────────
    def _make_arcs(items, count_key='count'):
        """Build arc_len/arc_offset values for an SVG donut (circumference ~75.4)."""
        circ = 75.4
        total = sum(item[count_key] for item in items) or 1
        arcs = []
        offset = 0
        for item in items[:4]:
            arc = round((item[count_key] / total) * circ, 1)
            arcs.append({'arc_len': arc, 'gap': round(circ - arc, 1), 'offset': round(-offset, 1)})
            offset += arc
        return arcs

    # ── Additional task metrics ──────────────────────────────────────────────
    tasks_by_workspace_rows = list(
        period_qs.values(name=F('workspace__name'))
        .annotate(count=Count('id')).order_by('-count')[:10]
    )
    tasks_by_list_rows = list(
        period_qs.values(name=F('task_list__name'))
        .annotate(count=Count('id')).order_by('-count')[:10]
    )
    tasks_by_category_rows = list(
        period_qs.exclude(category='').values(name=F('category'))
        .annotate(count=Count('id')).order_by('-count')[:10]
    )
    tasks_ws_arcs = _make_arcs(tasks_by_workspace_rows[:4])
    tasks_list_arcs = _make_arcs(tasks_by_list_rows[:4])
    tasks_cat_arcs = _make_arcs(tasks_by_category_rows[:4])

    # ── Subtask metrics ────────────────────────────────────────────────────
    sub_base = Subtask.objects.filter(task__in=base_qs)
    if period_days is not None:
        sub_qs = sub_base.filter(created_at__date__gte=period_start)
    else:
        sub_qs = sub_base
    total_subtasks = sub_qs.count()
    done_subtasks = sub_qs.filter(is_done=True).count()
    open_subtasks = total_subtasks - done_subtasks
    subtask_completion = round((done_subtasks / total_subtasks) * 100) if total_subtasks else 0
    subtask_overdue = sub_qs.filter(is_done=False, due_date__lt=today).count()
    subtask_unassigned = sub_qs.filter(assignees__isnull=True).count()
    subtask_no_due = sub_qs.filter(due_date__isnull=True).count()
    subtask_due_soon_count = sub_qs.filter(is_done=False, due_date__gte=today, due_date__lte=today + timedelta(days=14)).count()
    subtask_statuses_list = []
    for k, label in Subtask.STATUS_CHOICES:
        cnt = sub_qs.filter(status=k).count()
        subtask_statuses_list.append({'key': k, 'label': label, 'count': cnt})
    subtask_priority_list = []
    for k, label in Subtask.PRIORITY_CHOICES:
        cnt = sub_qs.filter(priority=k).count()
        subtask_priority_list.append({'key': k, 'label': label, 'count': cnt})
    subtask_assignee_rows = list(
        sub_qs.exclude(assignees__isnull=True)
        .values(name=F('assignees__first_name'))
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    for r in subtask_assignee_rows:
        if not r['name']:
            r['name'] = 'Unknown'

    # Subtask by workspace
    subtask_by_workspace_rows = list(
        sub_qs.values(name=F('task__workspace__name'))
        .annotate(count=Count('id')).order_by('-count')[:10]
    )
    subtask_by_list_rows = list(
        sub_qs.values(name=F('task__task_list__name'))
        .annotate(count=Count('id')).order_by('-count')[:10]
    )
    subtask_by_parent_status_rows = list(
        sub_qs.values(name=F('task__status'))
        .annotate(count=Count('id')).order_by('-count')
    )
    # Map status keys to labels
    _status_map = dict(Task.STATUS_CHOICES)
    for r in subtask_by_parent_status_rows:
        r['name'] = _status_map.get(r['name'], r['name'])
    subtask_by_category_rows = list(
        sub_qs.exclude(category='').values(name=F('category'))
        .annotate(count=Count('id')).order_by('-count')[:10]
    )
    subtask_overdue_qs = list(
        sub_qs.filter(is_done=False, due_date__lt=today)
        .select_related('task').order_by('due_date')[:20]
    )
    subtask_due_soon_qs = list(
        sub_qs.filter(is_done=False, due_date__gte=today, due_date__lte=today + timedelta(days=14))
        .select_related('task').order_by('due_date')[:20]
    )
    subtask_recent_qs = list(
        sub_qs.select_related('task').order_by('-created_at')[:20]
    )
    subtask_ws_arcs = _make_arcs(subtask_by_workspace_rows[:4])
    subtask_list_arcs = _make_arcs(subtask_by_list_rows[:4])
    subtask_parent_arcs = _make_arcs(subtask_by_parent_status_rows[:4])
    subtask_cat_arcs = _make_arcs(subtask_by_category_rows[:4])

    status_arcs = _make_arcs(statuses_list)
    assignee_arcs = _make_arcs(assignee_rows[:4])
    priority_arcs = _make_arcs(priority_list)
    subtask_status_arcs = _make_arcs(subtask_statuses_list)
    subtask_priority_arcs = _make_arcs(subtask_priority_list)
    subtask_assignee_arcs = _make_arcs(subtask_assignee_rows[:4])

    period_label_map = {
        'daily': 'Today', 'weekly': 'Last 7 days',
        'monthly': 'Last 30 days', 'quarter': 'Last 90 days', 'all': 'All time',
    }

    return {
        'period': period,
        'period_label': period_label_map[period],
        'period_choices': [
            ('daily', 'Today'), ('weekly', '7 d'),
            ('monthly', '30 d'), ('quarter', '90 d'), ('all', 'All'),
        ],
        'today': today,
        'all_workspaces': workspaces,
        'selected_workspace': selected_ws,
        'selected_list': selected_list,
        'selected_workspaces': selected_workspaces,
        'selected_lists': selected_lists,
        'selected_ws_ids': selected_ws_ids,
        'selected_list_ids': selected_list_ids,
        'lists_in_ws': lists_in_ws,
        # KPI numbers
        'total_tasks': total_tasks,
        'open_tasks': open_tasks,
        'closed_tasks': closed_tasks,
        'completion_rate': completion_rate,
        'overdue': overdue,
        'overdue_pct': overdue_pct,
        'due_this_week': due_this_week,
        'unassigned_count': unassigned_count,
        'no_due_date_count': no_due_date_count,
        'in_progress_count': in_progress_count,
        'urgent_count': urgent_count,
        'total_tracked_label': _fmt_dur(total_seconds),
        'velocity': velocity,
        'avg_cycle_days': avg_cycle_days,
        # Breakdowns
        'statuses_list': statuses_list,
        'priority_list': priority_list,
        'team_rows': team_rows,
        'assignee_rows': assignee_rows,
        'overdue_tasks': overdue_tasks_qs,
        'due_soon_tasks': due_soon_tasks_qs,
        'recent_tasks': recent_tasks_qs,
        'category_rows': category_rows,
        'workspace_hour_rows': workspace_hour_rows,
        # Chart JSON
        'chart_labels_json': _json.dumps(chart_labels),
        'chart_created_json': _json.dumps(chart_created),
        'chart_done_json': _json.dumps(chart_done_data),
        # JSON versions for JS charts
        'statuses_json': _json.dumps([{'label': s['label'], 'count': s['count'], 'key': s['key']} for s in statuses_list]),
        'priority_json': _json.dumps([{'label': p['label'], 'count': p['count'], 'key': p['key']} for p in priority_list]),
        'assignee_json': _json.dumps(assignee_rows[:10]),
        'category_json': _json.dumps([{'label': c['label'], 'seconds': c['seconds'], 'time_label': c['time_label']} for c in category_rows]),
        'ws_hours_json': _json.dumps([{'name': r['name'], 'seconds': r['seconds'], 'time_label': r['time_label']} for r in workspace_hour_rows]),
        'trend_preview': trend_preview,
        'status_arcs': status_arcs,
        'assignee_arcs': assignee_arcs,
        'priority_arcs': priority_arcs,
        # Subtask metrics
        'total_subtasks': total_subtasks,
        'done_subtasks': done_subtasks,
        'open_subtasks': open_subtasks,
        'subtask_completion': subtask_completion,
        'subtask_overdue': subtask_overdue,
        'subtask_statuses_list': subtask_statuses_list,
        'subtask_priority_list': subtask_priority_list,
        'subtask_assignee_rows': subtask_assignee_rows,
        'subtask_status_arcs': subtask_status_arcs,
        'subtask_priority_arcs': subtask_priority_arcs,
        'subtask_assignee_arcs': subtask_assignee_arcs,
        # Additional task breakdowns
        'tasks_by_workspace_rows': tasks_by_workspace_rows,
        'tasks_by_list_rows': tasks_by_list_rows,
        'tasks_by_category_rows': tasks_by_category_rows,
        'tasks_ws_arcs': tasks_ws_arcs,
        'tasks_list_arcs': tasks_list_arcs,
        'tasks_cat_arcs': tasks_cat_arcs,
        'tasks_ws_json': _json.dumps(tasks_by_workspace_rows[:10]),
        'tasks_list_json': _json.dumps(tasks_by_list_rows[:10]),
        'tasks_cat_json': _json.dumps(tasks_by_category_rows[:10]),
        # Additional subtask breakdowns
        'subtask_unassigned': subtask_unassigned,
        'subtask_no_due': subtask_no_due,
        'subtask_due_soon_count': subtask_due_soon_count,
        'subtask_by_workspace_rows': subtask_by_workspace_rows,
        'subtask_by_list_rows': subtask_by_list_rows,
        'subtask_by_parent_status_rows': subtask_by_parent_status_rows,
        'subtask_by_category_rows': subtask_by_category_rows,
        'subtask_overdue_qs': subtask_overdue_qs,
        'subtask_due_soon_qs': subtask_due_soon_qs,
        'subtask_recent_qs': subtask_recent_qs,
        'subtask_ws_arcs': subtask_ws_arcs,
        'subtask_list_arcs': subtask_list_arcs,
        'subtask_parent_arcs': subtask_parent_arcs,
        'subtask_cat_arcs': subtask_cat_arcs,
        'subtask_ws_json': _json.dumps(subtask_by_workspace_rows[:10]),
        'subtask_list_json': _json.dumps(subtask_by_list_rows[:10]),
        'subtask_parent_json': _json.dumps(subtask_by_parent_status_rows[:10]),
        'subtask_cat_json': _json.dumps(subtask_by_category_rows[:10]),
        'subtask_statuses_json': _json.dumps([{'label': s['label'], 'count': s['count'], 'key': s['key']} for s in subtask_statuses_list]),
        'subtask_priority_json': _json.dumps([{'label': p['label'], 'count': p['count'], 'key': p['key']} for p in subtask_priority_list]),
        'subtask_assignee_json': _json.dumps(subtask_assignee_rows[:10]),
    }


# Reports / Dashboard
@login_required
def reports(request):
    # If a template is requested, restore its card layout
    template_param = request.GET.get('template', '')
    if template_param.isdigit():
        tpl = ReportTemplate.objects.filter(id=int(template_param), user=request.user).first()
        if tpl and tpl.card_layout:
            DashboardCard.objects.filter(user=request.user).delete()
            for item in tpl.card_layout:
                if item.get('card_type') in CARD_CATALOG:
                    DashboardCard.objects.create(
                        user=request.user,
                        card_type=item['card_type'],
                        position=item.get('position', 0),
                        width=item.get('width', 'half'),
                    )

    cards = list(DashboardCard.objects.filter(user=request.user))
    data = _compute_dashboard_data(request)

    # Annotate each card with catalog metadata
    for card in cards:
        card.meta = CARD_CATALOG.get(card.card_type, {'label': card.card_type, 'desc': ''})

    saved_templates = list(ReportTemplate.objects.filter(user=request.user))
    # Detect which template is currently active
    active_template_id = int(template_param) if template_param.isdigit() else None
    if not active_template_id:
        # Fallback: match by filters
        cur_ws_ids = sorted(data.get('selected_ws_ids', set()))
        cur_list_ids = sorted(data.get('selected_list_ids', set()))
        cur_period = data.get('period', 'monthly')
        for tpl in saved_templates:
            if (sorted(tpl.workspace_ids) == cur_ws_ids
                    and sorted(tpl.list_ids) == cur_list_ids
                    and tpl.period == cur_period):
                active_template_id = tpl.id
                break

    data.update({
        'active_nav': 'reports',
        'dashboard_cards': cards,
        'catalog_groups': _card_catalog_grouped(),
        'saved_templates': saved_templates,
        'active_template_id': active_template_id,
    })
    data.update(_nav_context(request.user, request=request))

    return render(request, 'workspaces/reports.html', data)


@login_required
@require_POST
def dashboard_card_add(request):
    card_type = request.POST.get('card_type', '')
    if card_type not in CARD_CATALOG:
        return JsonResponse({'error': 'Invalid card type'}, status=400)
    meta = CARD_CATALOG[card_type]
    max_pos = DashboardCard.objects.filter(user=request.user).aggregate(Max('position'))['position__max']
    if max_pos is None:
        max_pos = -1
    card = DashboardCard.objects.create(
        user=request.user,
        card_type=card_type,
        position=max_pos + 1,
        width=meta.get('default_width', 'half'),
    )
    return JsonResponse({'id': card.id, 'card_type': card_type})


@login_required
@require_POST
def dashboard_card_remove(request, card_id):
    DashboardCard.objects.filter(id=card_id, user=request.user).delete()
    return JsonResponse({'ok': True})


@login_required
@require_POST
def dashboard_card_reorder(request):
    import json
    try:
        order = json.loads(request.body)['order']
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Bad request'}, status=400)
    for i, card_id in enumerate(order):
        DashboardCard.objects.filter(id=int(card_id), user=request.user).update(position=i)
    return JsonResponse({'ok': True})


@login_required
def dashboard_card_data(request):
    card_id = request.GET.get('card_id', '')
    if not card_id.isdigit():
        return JsonResponse({'error': 'Bad request'}, status=400)
    card = DashboardCard.objects.filter(id=int(card_id), user=request.user).first()
    if not card:
        return JsonResponse({'error': 'Not found'}, status=404)
    card.meta = CARD_CATALOG.get(card.card_type, {'label': card.card_type, 'desc': ''})
    data = _compute_dashboard_data(request)
    data['card'] = card
    return render(request, 'workspaces/_dashboard_card.html', data)


# ── Saved Report Templates ─────────────────────────────────────────────────
@login_required
@require_POST
def report_template_save(request):
    """Save or update a report template (named filter preset)."""
    name = request.POST.get('name', '').strip()
    template_type = request.POST.get('template_type', 'custom')
    if not name:
        return JsonResponse({'error': 'Name is required'}, status=400)
    if template_type not in dict(ReportTemplate.TYPE_CHOICES):
        template_type = 'custom'

    ws_ids = [int(x) for x in request.POST.getlist('workspace_ids') if x.isdigit()]
    list_ids = [int(x) for x in request.POST.getlist('list_ids') if x.isdigit()]
    period = request.POST.get('period', 'monthly')

    # Snapshot current dashboard card layout
    cards = DashboardCard.objects.filter(user=request.user).order_by('position')
    card_layout = [
        {'card_type': c.card_type, 'position': c.position, 'width': c.width}
        for c in cards
    ]

    tpl_id = request.POST.get('template_id', '')
    if tpl_id.isdigit():
        tpl = ReportTemplate.objects.filter(id=int(tpl_id), user=request.user).first()
        if tpl:
            tpl.name = name
            tpl.template_type = template_type
            tpl.workspace_ids = ws_ids
            tpl.list_ids = list_ids
            tpl.period = period
            tpl.card_layout = card_layout
            tpl.save()
            return JsonResponse({'id': tpl.id, 'name': tpl.name, 'updated': True})

    tpl = ReportTemplate.objects.create(
        user=request.user,
        name=name,
        template_type=template_type,
        workspace_ids=ws_ids,
        list_ids=list_ids,
        period=period,
        card_layout=card_layout,
    )
    return JsonResponse({'id': tpl.id, 'name': tpl.name, 'created': True})


@login_required
@require_POST
def report_template_delete(request, template_id):
    """Delete a saved report template."""
    ReportTemplate.objects.filter(id=template_id, user=request.user).delete()
    return JsonResponse({'ok': True})


VIEW_PREF_BOOL_FIELDS = {
    'show_empty_statuses', 'wrap_text', 'show_task_locations',
    'show_subtask_parent_names', 'show_closed_tasks',
    'is_pinned', 'is_favorite', 'is_private', 'is_default',
    'autosave_for_me', 'protected',
}
VIEW_PREF_TEXT_FIELDS = {'subtasks_mode'}


@login_required
@require_POST
def view_preference_set(request, list_id, view):
    tl = get_object_or_404(TaskList, pk=list_id, workspace__in=_accessible_workspaces(request.user))
    if view not in {k for k, _ in ViewPreference.VIEW_CHOICES}:
        return redirect('workspaces:list_detail', list_id=tl.pk)
    pref, _ = ViewPreference.objects.get_or_create(user=request.user, task_list=tl, view=view)
    for f in VIEW_PREF_BOOL_FIELDS:
        if f in request.POST:
            setattr(pref, f, request.POST.get(f) == '1')
    for f in VIEW_PREF_TEXT_FIELDS:
        if f in request.POST:
            val = request.POST.get(f, '')
            if f == 'subtasks_mode' and val in {k for k, _ in ViewPreference.SUBTASK_MODES}:
                pref.subtasks_mode = val
    pref.save()
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('workspaces:list_detail', list_id=tl.pk)


@login_required
@require_POST
def task_custom_value_set(request, task_id, field_id):
    task = get_object_or_404(Task, pk=task_id, workspace__in=_accessible_workspaces(request.user))
    field = get_object_or_404(CustomField, pk=field_id, workspace=task.workspace)
    value, _ = TaskCustomFieldValue.objects.get_or_create(task=task, field=field)
    if field.field_type == 'dropdown':
        opt_id = request.POST.get('option')
        if opt_id:
            opt = CustomFieldOption.objects.filter(field=field, pk=opt_id).first()
            value.option = opt
        else:
            value.option = None
    elif field.field_type == 'labels':
        opt_ids = [int(x) for x in request.POST.getlist('options') if x.isdigit()]
        value.option = None
        value.save()
        value.options.set(CustomFieldOption.objects.filter(field=field, pk__in=opt_ids))
    elif field.field_type == 'text' or field.field_type in ('url', 'email'):
        value.text_value = request.POST.get('value', '')
    elif field.field_type == 'number':
        raw = request.POST.get('value', '').strip()
        try:
            value.number_value = float(raw) if raw else None
        except ValueError:
            value.number_value = None
    elif field.field_type == 'date':
        raw = request.POST.get('value', '').strip()
        if raw:
            from datetime import datetime as _dt
            try:
                value.date_value = _dt.strptime(raw, '%Y-%m-%d').date()
            except ValueError:
                value.date_value = None
        else:
            value.date_value = None
    elif field.field_type == 'checkbox':
        value.bool_value = request.POST.get('value') == '1'
    value.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({'ok': True})
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or ''
    if next_url:
        return redirect(next_url)
    return redirect('workspaces:task_detail', task_id=task.pk)


# ── Notifications ───────────────────────────────────────────────────────────

@login_required
def notification_list(request):
    from django.http import JsonResponse
    notifications = (
        Notification.objects
        .filter(recipient=request.user)
        .select_related('actor', 'task')
        .order_by('-created_at')[:50]
    )
    data = []
    for n in notifications:
        data.append({
            'id': n.id,
            'actor': n.actor.get_full_name() or n.actor.username,
            'actor_initial': (n.actor.username or '?')[0].upper(),
            'verb': n.verb,
            'description': n.description,
            'task_id': n.task_id,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%b %d, %I:%M %p'),
        })
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'notifications': data, 'unread_count': unread_count})


@login_required
@require_POST
def notification_mark_read(request):
    from django.http import JsonResponse
    notif_id = request.POST.get('id')
    if notif_id == 'all':
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    elif notif_id:
        Notification.objects.filter(pk=notif_id, recipient=request.user).update(is_read=True)
    return JsonResponse({'ok': True})
