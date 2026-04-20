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
