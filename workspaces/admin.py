from django.contrib import admin

from .models import Task, Workspace

admin.site.register(Workspace)
admin.site.register(Task)
