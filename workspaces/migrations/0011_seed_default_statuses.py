from django.db import migrations


DEFAULTS = [
    ('todo', 'To Do', 'gray', 0, False),
    ('in_progress', 'In Progress', 'purple', 1, False),
    ('on_hold', 'On Hold / Waiting', 'pink', 2, False),
    ('review', 'Client Review', 'orange', 3, False),
    ('internal_review', 'Internal Review', 'red', 4, False),
    ('done', 'Done', 'green', 5, True),
]


def seed(apps, schema_editor):
    TaskList = apps.get_model('workspaces', 'TaskList')
    TaskStatus = apps.get_model('workspaces', 'TaskStatus')
    for tl in TaskList.objects.all():
        for key, name, color, position, is_done in DEFAULTS:
            TaskStatus.objects.get_or_create(
                task_list=tl, key=key,
                defaults={'name': name, 'color': color, 'position': position, 'is_done': is_done},
            )


def reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [('workspaces', '0010_taskstatus')]
    operations = [migrations.RunPython(seed, reverse)]
