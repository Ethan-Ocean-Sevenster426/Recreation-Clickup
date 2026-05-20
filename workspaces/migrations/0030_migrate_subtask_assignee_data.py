"""Copy existing Subtask.assignee FK values into the new Subtask.assignees M2M field."""

from django.db import migrations


def forwards(apps, schema_editor):
    Subtask = apps.get_model('workspaces', 'Subtask')
    for st in Subtask.objects.filter(assignee__isnull=False):
        st.assignees.add(st.assignee_id)


def backwards(apps, schema_editor):
    Subtask = apps.get_model('workspaces', 'Subtask')
    for st in Subtask.objects.prefetch_related('assignees'):
        first = st.assignees.first()
        if first:
            st.assignee = first
            st.save(update_fields=['assignee'])


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0029_subtask_add_assignees_m2m'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
