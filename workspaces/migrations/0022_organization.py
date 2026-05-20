import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def create_default_orgs(apps, schema_editor):
    """Create one default Organization per workspace owner and link existing spaces."""
    Workspace = apps.get_model('workspaces', 'Workspace')
    Organization = apps.get_model('workspaces', 'Organization')
    User = apps.get_model('main', 'User')

    owner_ids = set(Workspace.objects.values_list('owner_id', flat=True))
    for owner_id in owner_ids:
        try:
            user = User.objects.get(pk=owner_id)
            org_name = f"{user.username}'s Workspace"
        except User.DoesNotExist:
            org_name = 'My Workspace'

        org = Organization.objects.create(name=org_name, owner_id=owner_id)
        Workspace.objects.filter(owner_id=owner_id).update(organization=org)


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0021_task_created_by'),
        ('main', '0002_user_theme'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organizations', to=settings.AUTH_USER_MODEL)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='workspace',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='spaces', to='workspaces.organization'),
        ),
        migrations.RunPython(create_default_orgs, migrations.RunPython.noop),
    ]
