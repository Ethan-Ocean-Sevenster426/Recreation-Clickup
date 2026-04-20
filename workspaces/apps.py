from django.apps import AppConfig
from django.db.models.signals import post_save


class WorkspacesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workspaces'

    def ready(self):
        from .models import DEFAULT_STATUSES, TaskList, TaskStatus

        def seed_default_statuses(sender, instance, created, **kwargs):
            if not created:
                return
            for key, name, color, position, is_done in DEFAULT_STATUSES:
                TaskStatus.objects.get_or_create(
                    task_list=instance, key=key,
                    defaults={'name': name, 'color': color, 'position': position, 'is_done': is_done},
                )

        post_save.connect(seed_default_statuses, sender=TaskList, dispatch_uid='seed_default_statuses')
