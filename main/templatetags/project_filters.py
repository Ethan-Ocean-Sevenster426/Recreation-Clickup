# main/templatetags/project_filters.py
from django import template
from django.db.models import Avg, Q
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def filter_status(projects, status):
    """Filter projects by status"""
    if not projects or not status:
        return projects
    return projects.filter(status=status)

@register.filter
def avg_progress(projects):
    """Calculate average progress of all projects"""
    if not projects:
        return 0
    
    # Handle QuerySet
    if hasattr(projects, 'aggregate'):
        avg = projects.aggregate(avg_progress=Avg('progress'))['avg_progress']
        return int(avg) if avg else 0
    
    # Handle list/iterable
    try:
        total = sum(project.progress for project in projects)
        return int(total / len(projects)) if projects else 0
    except (AttributeError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def count_by_status(projects, status):
    """Count projects by status"""
    if not projects or not status:
        return 0
    
    # Handle QuerySet
    if hasattr(projects, 'filter'):
        return projects.filter(status=status).count()
    
    # Handle list/iterable
    try:
        return sum(1 for project in projects if project.status == status)
    except (AttributeError, TypeError):
        return 0

@register.filter
def count_active(projects):
    """Count active (in-progress) projects"""
    return count_by_status(projects, 'in-progress')

@register.filter
def count_completed(projects):
    """Count completed projects"""
    return count_by_status(projects, 'completed')

@register.filter
def count_planning(projects):
    """Count planning projects"""
    return count_by_status(projects, 'planning')

@register.filter
def project_progress_color(status):
    """Return CSS class for progress bar based on status"""
    status_colors = {
        'completed': 'bg-green-500',
        'in-progress': 'bg-blue-500',
        'planning': 'bg-yellow-500',
        'on-hold': 'bg-gray-500',
    }
    return status_colors.get(status, 'bg-gray-500')

@register.filter
def status_badge_class(status):
    """Return CSS classes for status badges"""
    status_classes = {
        'completed': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
        'in-progress': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
        'planning': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
        'on-hold': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
    }
    return status_classes.get(status, 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200')

@register.filter
def priority_badge_class(priority):
    """Return CSS classes for priority badges"""
    priority_classes = {
        'high': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
        'medium': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
        'low': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    }
    return priority_classes.get(priority, 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200')

@register.filter
def priority_emoji(priority):
    """Return emoji for priority level"""
    priority_emojis = {
        'high': '🔴',
        'medium': '🟡',
        'low': '🟢',
    }
    return priority_emojis.get(priority, '⚪')

@register.filter
def truncate_smart(value, length):
    """Smart truncate that doesn't cut words"""
    if not value or len(value) <= length:
        return value
    
    truncated = value[:length]
    # Find the last space to avoid cutting words
    last_space = truncated.rfind(' ')
    if last_space > length * 0.8:  # Only if we're not cutting too much
        truncated = truncated[:last_space]
    
    return truncated + '...'

@register.filter
def first_letter(value):
    """Get first letter of a string, uppercase"""
    if not value:
        return ''
    return str(value)[0].upper()

@register.filter
def team_count(project):
    """Get team member count for a project"""
    try:
        return project.team.count()
    except AttributeError:
        return 0

@register.filter
def pluralize_custom(value, arg="s"):
    """Custom pluralize filter"""
    try:
        count = int(value)
        if count == 1:
            return ""
        return arg
    except (ValueError, TypeError):
        return arg

@register.filter
def calculate_days_remaining(end_date):
    """Calculate days remaining until project end date"""
    from datetime import date
    
    if not end_date:
        return "N/A"
    
    try:
        today = date.today()
        if end_date < today:
            return "Overdue"
        
        delta = end_date - today
        days = delta.days
        
        if days == 0:
            return "Due Today"
        elif days == 1:
            return "1 day"
        else:
            return f"{days} days"
    except (AttributeError, TypeError):
        return "N/A"

@register.simple_tag
def project_stats(projects):
    """Calculate comprehensive project statistics"""
    if not projects:
        return {
            'total': 0,
            'active': 0,
            'completed': 0,
            'planning': 0,
            'avg_progress': 0
        }
    
    stats = {
        'total': len(projects) if hasattr(projects, '__len__') else projects.count(),
        'active': count_active(projects),
        'completed': count_completed(projects),
        'planning': count_planning(projects),
        'avg_progress': avg_progress(projects)
    }
    
    return stats

@register.inclusion_tag('components/progress_bar.html')
def progress_bar(progress, status='in-progress', show_percentage=True):
    """Render a progress bar component"""
    return {
        'progress': progress,
        'status': status,
        'show_percentage': show_percentage,
        'color_class': project_progress_color(status)
    }

@register.inclusion_tag('components/status_badge.html')
def status_badge(status):
    """Render a status badge component"""
    return {
        'status': status,
        'display_text': status.replace('-', ' ').title(),
        'css_class': status_badge_class(status)
    }

@register.inclusion_tag('components/priority_badge.html')
def priority_badge(priority):
    """Render a priority badge component"""
    return {
        'priority': priority,
        'display_text': priority.title(),
        'emoji': priority_emoji(priority),
        'css_class': priority_badge_class(priority)
    }

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key)