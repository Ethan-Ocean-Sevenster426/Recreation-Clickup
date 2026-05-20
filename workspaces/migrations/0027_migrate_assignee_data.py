"""Copy existing Task.assignee FK values into the new Task.assignees M2M field."""

from django.db import migrations


def forwards(apps, schema_editor):
    Task = apps.get_model('workspaces', 'Task')
    for task in Task.objects.filter(assignee__isnull=False):
        task.assignees.add(task.assignee_id)


def backwards(apps, schema_editor):
    Task = apps.get_model('workspaces', 'Task')
    for task in Task.objects.prefetch_related('assignees'):
        first = task.assignees.first()
        if first:
            task.assignee = first
            task.save(update_fields=['assignee'])


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0026_task_assignees_m2m'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
