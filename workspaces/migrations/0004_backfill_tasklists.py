from django.db import migrations


def backfill(apps, schema_editor):
    Workspace = apps.get_model('workspaces', 'Workspace')
    TaskList = apps.get_model('workspaces', 'TaskList')
    Task = apps.get_model('workspaces', 'Task')

    for ws in Workspace.objects.all():
        default_list, _ = TaskList.objects.get_or_create(
            workspace=ws, name='General', defaults={'icon': '📋'},
        )
        Task.objects.filter(workspace=ws, task_list__isnull=True).update(task_list=default_list)


def reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('workspaces', '0003_tasklist_task_task_list'),
    ]
    operations = [
        migrations.RunPython(backfill, reverse),
    ]
