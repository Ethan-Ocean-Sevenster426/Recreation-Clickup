import calendar as _cal
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from django.utils import timezone

from django.contrib import messages
from django.db.models import Q

from .models import (
    STATUS_COLORS, Subtask, Task, TaskComment, TaskList, TaskStatus, TimeEntry,
    Workspace, WorkspaceMember,
)

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


def _accessible_workspaces(user):
    """Workspaces the user owns OR is a member of."""
    return Workspace.objects.filter(Q(owner=user) | Q(memberships__user=user)).distinct()


def _user_role(user, workspace):
    """Returns 'owner', 'editor', 'viewer', or None."""
    if workspace.owner_id == user.id:
        return 'owner'
    m = WorkspaceMember.objects.filter(workspace=workspace, user=user).first()
    return m.role if m else None


def _nav_context(user, active_workspace=None, active_list=None):
    return {
        'nav_workspaces': _accessible_workspaces(user).prefetch_related('lists'),
        'active_workspace': active_workspace,
        'active_list': active_list,
        'status_colors': STATUS_COLORS,
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


def _columns(task_list):
    return [
        {
            'status': s,
            'key': s.key,
            'label': s.name,
            'color': s.color,
            'tasks': list(task_list.tasks.filter(status=s.key)),
        }
        for s in task_list.statuses.all()
    ]


def _status_choices(task_list):
    return [(s.key, s.name) for s in task_list.statuses.all()]


# Workspaces
@login_required
def workspace_list(request):
    return render(request, 'workspaces/list.html', {
        'workspaces': _accessible_workspaces(request.user),
        **_nav_context(request.user),
    })


@login_required
@require_POST
def workspace_create(request):
    name = (request.POST.get('name') or '').strip()
    if name:
        Workspace.objects.create(name=name, owner=request.user)
    return redirect('workspaces:list')


@login_required
@require_POST
def workspace_delete(request, workspace_id):
    ws = get_object_or_404(_accessible_workspaces(request.user), pk=workspace_id)
    ws.delete()
    return redirect('workspaces:list')


@login_required
def workspace_detail(request, workspace_id):
    ws = get_object_or_404(_accessible_workspaces(request.user), pk=workspace_id)
    return render(request, 'workspaces/workspace_detail.html', {
        'workspace': ws,
        'status_colors': STATUS_COLORS,
        **_nav_context(request.user, active_workspace=ws),
    })


# Lists
@login_required
@require_POST
def list_create(request, workspace_id):
    ws = get_object_or_404(_accessible_workspaces(request.user), pk=workspace_id)
    name = (request.POST.get('name') or '').strip()
    if name:
        TaskList.objects.create(
            workspace=ws, name=name,
            icon=(request.POST.get('icon') or '📋')[:8],
        )
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
    if color not in dict(STATUS_COLORS):
        color = tl.color
    if name:
        tl.name = name
    tl.color = color
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


def _task_list_context(tl):
    return {
        'workspace': tl.workspace,
        'task_list': tl,
        'columns': _columns(tl),
        'priority_choices': Task.PRIORITY_CHOICES,
        'status_choices': _status_choices(tl),
        'status_colors': STATUS_COLORS,
        'users': User.objects.all().order_by('username'),
    }


@login_required
def list_detail(request, list_id):
    tl = get_object_or_404(TaskList, pk=list_id, workspace__in=_accessible_workspaces(request.user))
    return render(request, 'workspaces/detail.html', {
        **_task_list_context(tl),
        'view': 'list',
        **_nav_context(request.user, active_workspace=tl.workspace, active_list=tl),
    })


@login_required
def list_board(request, list_id):
    tl = get_object_or_404(TaskList, pk=list_id, workspace__in=_accessible_workspaces(request.user))
    return render(request, 'workspaces/board.html', {
        **_task_list_context(tl),
        'view': 'board',
        **_nav_context(request.user, active_workspace=tl.workspace, active_list=tl),
    })


@login_required
def list_calendar(request, list_id):
    tl = get_object_or_404(TaskList, pk=list_id, workspace__in=_accessible_workspaces(request.user))
    today = date.today()
    try:
        year = int(request.GET.get('year') or today.year)
        month = int(request.GET.get('month') or today.month)
    except ValueError:
        year, month = today.year, today.month

    cal_iter = _cal.Calendar(firstweekday=6)  # Sunday-first
    weeks_dates = cal_iter.monthdatescalendar(year, month)

    tasks = list(tl.tasks.all())
    week_rows = []
    for week_days in weeks_dates:
        wk_start, wk_end = week_days[0], week_days[6]
        bars = []
        for t in tasks:
            start, end = _task_range(t, today)
            if not start:
                continue
            if not end:
                end = start
            if end < wk_start or start > wk_end:
                continue
            bar_start = max(start, wk_start)
            bar_end = min(end, wk_end)
            bars.append({
                'task': t,
                'col_start': (bar_start - wk_start).days + 1,
                'col_end': (bar_end - wk_start).days + 2,
            })
        lane_count = _assign_lanes(bars)
        week_rows.append({
            'days': [{'date': d, 'in_month': d.month == month, 'is_today': d == today} for d in week_days],
            'bars': bars,
            'lane_count': lane_count,
        })

    prev_y, prev_m = (year, month - 1) if month > 1 else (year - 1, 12)
    next_y, next_m = (year, month + 1) if month < 12 else (year + 1, 1)

    unscheduled = [t for t in tasks if not (t.start_date or t.due_date)]
    overdue = [t for t in tasks if t.due_date and t.due_date < today and t.status != 'done']

    return render(request, 'workspaces/calendar.html', {
        **_task_list_context(tl),
        'view': 'calendar',
        'week_rows': week_rows,
        'month_name': date(year, month, 1).strftime('%B %Y'),
        'year': year,
        'month': month,
        'prev_year': prev_y,
        'prev_month': prev_m,
        'next_year': next_y,
        'next_month': next_m,
        'day_names': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        'unscheduled_count': len(unscheduled),
        'overdue_count': len(overdue),
        **_nav_context(request.user, active_workspace=tl.workspace, active_list=tl),
    })


@login_required
def list_gantt(request, list_id):
    tl = get_object_or_404(TaskList, pk=list_id, workspace__in=_accessible_workspaces(request.user))
    today = date.today()
    tasks = list(tl.tasks.all())

    dated = [(t, *_task_range(t, today)) for t in tasks]
    dated = [(t, s, e) for t, s, e in dated if s]

    if dated:
        range_start = min(s for _, s, _ in dated) - timedelta(days=3)
        range_end = max((e or s) for _, s, e in dated) + timedelta(days=3)
    else:
        range_start = today - timedelta(days=7)
        range_end = today + timedelta(days=21)

    if (range_end - range_start).days < 28:
        range_end = range_start + timedelta(days=28)

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

    rows = []
    for t, s, e in dated:
        end = e or s
        left_days = (s - range_start).days
        span_days = (end - s).days + 1
        rows.append({
            'task': t,
            'left_days': left_days,
            'span_days': span_days,
        })
    # Also include undated tasks at bottom with a collapse indicator
    for t in tasks:
        if not (t.start_date or t.due_date):
            rows.append({'task': t, 'left_days': None, 'span_days': None})

    today_offset = (today - range_start).days if range_start <= today <= range_end else None

    return render(request, 'workspaces/gantt.html', {
        **_task_list_context(tl),
        'view': 'gantt',
        'days': days,
        'weeks': weeks,
        'total_days': total_days,
        'rows': rows,
        'today_offset': today_offset,
        **_nav_context(request.user, active_workspace=tl.workspace, active_list=tl),
    })


# Tasks
@login_required
@require_POST
def task_create(request, list_id):
    tl = get_object_or_404(TaskList, pk=list_id, workspace__in=_accessible_workspaces(request.user))
    title = (request.POST.get('title') or '').strip()
    if title:
        assignee_id = request.POST.get('assignee') or None
        assignee = User.objects.filter(pk=assignee_id).first() if assignee_id else None
        Task.objects.create(
            workspace=tl.workspace,
            task_list=tl,
            title=title,
            description=request.POST.get('description', ''),
            status=request.POST.get('status', 'todo'),
            priority=request.POST.get('priority', 'normal'),
            start_date=request.POST.get('start_date') or None,
            due_date=request.POST.get('due_date') or None,
            assignee=assignee,
            tags=request.POST.get('tags', '').strip(),
        )
    next_url = request.POST.get('next') or ''
    if next_url.startswith('/'):
        return redirect(next_url)
    return redirect('workspaces:list_detail', list_id=tl.pk)


@login_required
@require_POST
def task_update_status(request, task_id):
    task = get_object_or_404(Task, pk=task_id, workspace__in=_accessible_workspaces(request.user))
    new_status = request.POST.get('status')
    valid_keys = set(task.task_list.statuses.values_list('key', flat=True))
    if new_status in valid_keys:
        task.status = new_status
        task.save(update_fields=['status'])
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
    task.delete()
    return redirect('workspaces:list_detail', list_id=list_id)


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id, workspace__in=_accessible_workspaces(request.user))
    tl = task.task_list
    entries = task.time_entries.all()
    now = timezone.now()
    total_seconds = sum(e.duration_seconds(now) for e in entries)
    running = task.time_entries.filter(user=request.user, ended_at__isnull=True).first()
    return render(request, 'workspaces/task_detail.html', {
        **_task_list_context(tl),
        'task': task,
        'subtasks': task.subtasks.all(),
        'comments': task.comments.select_related('author').all(),
        'total_tracked_seconds': total_seconds,
        'running_entry': running,
        'running_started_at': running.started_at.isoformat() if running else '',
        **_nav_context(request.user, active_workspace=tl.workspace, active_list=tl),
    })


@login_required
@require_POST
def task_update(request, task_id):
    task = get_object_or_404(Task, pk=task_id, workspace__in=_accessible_workspaces(request.user))
    field = request.POST.get('field')
    value = request.POST.get('value', '')
    allowed = {'title', 'description', 'status', 'priority', 'start_date', 'due_date', 'tags', 'assignee', 'estimated_minutes'}
    if field not in allowed:
        return redirect('workspaces:task_detail', task_id=task.pk)

    if field == 'status':
        valid_keys = set(task.task_list.statuses.values_list('key', flat=True))
        if value not in valid_keys:
            return redirect('workspaces:task_detail', task_id=task.pk)
    if field == 'priority' and value not in dict(Task.PRIORITY_CHOICES):
        return redirect('workspaces:task_detail', task_id=task.pk)

    if field in {'start_date', 'due_date'}:
        setattr(task, field, value or None)
    elif field == 'assignee':
        task.assignee = User.objects.filter(pk=value).first() if value else None
    elif field == 'estimated_minutes':
        task.estimated_minutes = int(value) if value.isdigit() else None
    else:
        setattr(task, field, value)
    task.save()
    return redirect('workspaces:task_detail', task_id=task.pk)


@login_required
@require_POST
def subtask_create(request, task_id):
    task = get_object_or_404(Task, pk=task_id, workspace__in=_accessible_workspaces(request.user))
    title = (request.POST.get('title') or '').strip()
    if title:
        Subtask.objects.create(task=task, title=title)
    return redirect('workspaces:task_detail', task_id=task.pk)


@login_required
@require_POST
def subtask_toggle(request, subtask_id):
    st = get_object_or_404(Subtask, pk=subtask_id, task__workspace__in=_accessible_workspaces(request.user))
    st.is_done = not st.is_done
    st.save(update_fields=['is_done'])
    return redirect('workspaces:task_detail', task_id=st.task_id)


@login_required
@require_POST
def subtask_delete(request, subtask_id):
    st = get_object_or_404(Subtask, pk=subtask_id, task__workspace__in=_accessible_workspaces(request.user))
    task_id = st.task_id
    st.delete()
    return redirect('workspaces:task_detail', task_id=task_id)


@login_required
@require_POST
def comment_create(request, task_id):
    task = get_object_or_404(Task, pk=task_id, workspace__in=_accessible_workspaces(request.user))
    body = (request.POST.get('body') or '').strip()
    if body:
        TaskComment.objects.create(task=task, author=request.user, body=body)
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
    raw = (request.POST.get('minutes') or '').strip()
    try:
        minutes = int(raw)
    except ValueError:
        minutes = 0
    if minutes > 0:
        now = timezone.now()
        TimeEntry.objects.create(
            task=task, user=request.user,
            started_at=now,
            ended_at=now + timezone.timedelta(minutes=minutes),
            is_manual=True,
        )
    return redirect('workspaces:task_detail', task_id=task.pk)


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


@login_required
@_staff_required
def user_list(request):
    users = User.objects.all().order_by('username')
    return render(request, 'workspaces/users.html', {
        'users_all': users,
        **_nav_context(request.user),
    })


@login_required
@_staff_required
@require_POST
def user_create(request):
    username = (request.POST.get('username') or '').strip()
    email = (request.POST.get('email') or '').strip()
    password = (request.POST.get('password') or '').strip()
    first_name = (request.POST.get('first_name') or '').strip()
    last_name = (request.POST.get('last_name') or '').strip()
    if username and password and not User.objects.filter(username=username).exists():
        u = User.objects.create_user(username=username, email=email, password=password,
                                     first_name=first_name, last_name=last_name)
        if request.POST.get('is_staff') == '1':
            u.is_staff = True
            u.save(update_fields=['is_staff'])
        messages.success(request, f"User {username} created.")
    else:
        messages.error(request, "Username already exists or required fields missing.")
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
@_staff_required
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
@_staff_required
@require_POST
def user_delete(request, user_id):
    u = get_object_or_404(User, pk=user_id)
    if u.pk == request.user.pk:
        messages.error(request, "You can't delete yourself.")
    else:
        u.delete()
    return redirect('workspaces:user_list')


# ---------- Workspace members (access rights per workspace) ----------

@login_required
def workspace_members(request, workspace_id):
    ws = get_object_or_404(_accessible_workspaces(request.user), pk=workspace_id)
    memberships = ws.memberships.select_related('user').all()
    member_user_ids = {m.user_id for m in memberships} | {ws.owner_id}
    available_users = User.objects.exclude(pk__in=member_user_ids).order_by('username')
    current_role = _user_role(request.user, ws)
    return render(request, 'workspaces/members.html', {
        'workspace': ws,
        'memberships': memberships,
        'available_users': available_users,
        'role_choices': WorkspaceMember.ROLE_CHOICES,
        'current_role': current_role,
        **_nav_context(request.user, active_workspace=ws),
    })


@login_required
@require_POST
def workspace_member_add(request, workspace_id):
    ws = get_object_or_404(_accessible_workspaces(request.user), pk=workspace_id)
    if _user_role(request.user, ws) != 'owner':
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Only the workspace owner can add members.")
    user_id = request.POST.get('user_id')
    role = request.POST.get('role', 'editor')
    if role not in dict(WorkspaceMember.ROLE_CHOICES):
        role = 'editor'
    user = User.objects.filter(pk=user_id).first()
    if user and user.pk != ws.owner_id:
        WorkspaceMember.objects.get_or_create(workspace=ws, user=user, defaults={'role': role})
    return redirect('workspaces:members', workspace_id=ws.pk)


@login_required
@require_POST
def workspace_member_update(request, member_id):
    m = get_object_or_404(WorkspaceMember, pk=member_id)
    ws = m.workspace
    if ws.owner_id != request.user.id:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Only the workspace owner can change roles.")
    role = request.POST.get('role', m.role)
    if role in dict(WorkspaceMember.ROLE_CHOICES):
        m.role = role
        m.save(update_fields=['role'])
    return redirect('workspaces:members', workspace_id=ws.pk)


@login_required
@require_POST
def workspace_member_remove(request, member_id):
    m = get_object_or_404(WorkspaceMember, pk=member_id)
    ws = m.workspace
    if ws.owner_id != request.user.id and m.user_id != request.user.id:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Only the owner or the member themselves can remove this membership.")
    m.delete()
    return redirect('workspaces:members', workspace_id=ws.pk)
