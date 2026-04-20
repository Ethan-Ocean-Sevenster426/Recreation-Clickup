from django.conf import settings
from django.db import models


class Workspace(models.Model):
    name = models.CharField(max_length=120)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workspaces')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class WorkspaceMember(models.Model):
    ROLE_CHOICES = [
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workspace_memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='editor')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('workspace', 'user')]
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user} @ {self.workspace} ({self.role})"


class TaskList(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='lists')
    name = models.CharField(max_length=120)
    icon = models.CharField(max_length=8, blank=True, default='📋')
    color = models.CharField(max_length=20, default='blue')
    image = models.ImageField(upload_to='list_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.name


DEFAULT_STATUSES = [
    ('todo', 'To Do', 'gray', 0, False),
    ('in_progress', 'In Progress', 'purple', 1, False),
    ('on_hold', 'On Hold / Waiting', 'pink', 2, False),
    ('review', 'Client Review', 'orange', 3, False),
    ('internal_review', 'Internal Review', 'red', 4, False),
    ('done', 'Done', 'green', 5, True),
]

STATUS_COLORS = [
    ('gray', 'Gray'),
    ('purple', 'Purple'),
    ('pink', 'Pink'),
    ('orange', 'Orange'),
    ('red', 'Red'),
    ('green', 'Green'),
    ('blue', 'Blue'),
    ('yellow', 'Yellow'),
]


class TaskStatus(models.Model):
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name='statuses')
    key = models.CharField(max_length=40)
    name = models.CharField(max_length=60)
    color = models.CharField(max_length=20, default='gray')
    position = models.PositiveIntegerField(default=0)
    is_done = models.BooleanField(default=False)

    class Meta:
        ordering = ['position', 'id']
        unique_together = [('task_list', 'key')]

    def __str__(self):
        return f"{self.task_list.name} · {self.name}"


class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold / Waiting'),
        ('review', 'Client Review'),
        ('internal_review', 'Internal Review'),
        ('done', 'Done'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='tasks')
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='workspace_tasks')
    tags = models.CharField(max_length=255, blank=True, default='')
    estimated_minutes = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def tag_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]


class Subtask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=200)
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class TimeEntry(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_entries')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='time_entries')
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    is_manual = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-started_at']

    @property
    def is_running(self):
        return self.ended_at is None

    def duration_seconds(self, now=None):
        from django.utils import timezone
        end = self.ended_at or (now or timezone.now())
        return max(0, int((end - self.started_at).total_seconds()))

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
