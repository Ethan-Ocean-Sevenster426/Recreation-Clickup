from django import template

register = template.Library()


@register.filter
def status_color(task, task_list):
    """Return the color name for a task's status within its list. Falls back to gray."""
    if not task or not task_list:
        return 'gray'
    for s in task_list.statuses.all():
        if s.key == task.status:
            return s.color
    return 'gray'


@register.filter
def status_name(task, task_list):
    if not task or not task_list:
        return ''
    for s in task_list.statuses.all():
        if s.key == task.status:
            return s.name
    return task.status


@register.filter
def dict_get(d, key):
    """Look up `key` in dict `d`, supporting nested lookups via 'a.b.c' if needed.
    Returns '' if not found."""
    if d is None:
        return ''
    if isinstance(d, dict):
        return d.get(key, '')
    return ''


@register.filter
def cf_value(values_by_task, task_id):
    """Return the dict of {field_id: value} for a task, or {}."""
    if not isinstance(values_by_task, dict):
        return {}
    return values_by_task.get(task_id, {})


@register.filter
def humanize_key(value):
    """Turn a slug like 'on_hold' into 'On Hold'."""
    if not value:
        return ''
    return value.replace('_', ' ').title()


@register.filter
def days_taken(task):
    """Count distinct calendar days where time was tracked on this task."""
    if not task:
        return 0
    return task.time_entries.filter(deleted_at__isnull=True).dates('started_at', 'day').count()


@register.filter
def fmt_duration(seconds):
    """Format a number of seconds as Xh Ym Zs."""
    try:
        s = int(seconds)
    except (TypeError, ValueError):
        return '—'
    if s <= 0:
        return '0s'
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    parts = []
    if h:
        parts.append(f'{h}h')
    if m:
        parts.append(f'{m}m')
    if sec or not parts:
        parts.append(f'{sec}s')
    return ' '.join(parts)
