from django.conf import settings
from django.db import models


class Organization(models.Model):
    """Top-level Workspace (organization) — a user can own/belong to multiple."""
    name = models.CharField(max_length=120)
    image = models.ImageField(upload_to='org_images/', null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organizations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Workspace(models.Model):
    PURPOSE_CHOICES = [
        ('work', 'Work'),
        ('project', 'Project'),
        ('retainer', 'Retainer'),
        ('personal', 'Personal'),
    ]
    name = models.CharField(max_length=120)
    icon = models.CharField(max_length=8, blank=True, default='')
    image = models.ImageField(upload_to='workspace_images/', null=True, blank=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, blank=True, default='')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workspaces')
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name='spaces')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


DEFAULT_CATEGORIES = [
    ('administration', 'Administration', 'blue'),
    ('development', 'Development', 'purple'),
    ('design', 'Design', 'pink'),
    ('meetings', 'Meetings', 'orange'),
    ('research', 'Research', 'green'),
    ('support', 'Support', 'yellow'),
    ('strategy', 'Strategy', 'red'),
    ('other', 'Other', 'gray'),
]


class Category(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='categories')
    key = models.SlugField(max_length=50)
    name = models.CharField(max_length=60)
    color = models.CharField(max_length=20, default='blue')
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position', 'name']
        unique_together = [('workspace', 'key')]

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


class ListMember(models.Model):
    """Tracks which lists within a workspace a user can access."""
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='list_memberships')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('task_list', 'user')]
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user} @ {self.task_list}"


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
    CATEGORY_CHOICES = [
        ('administration', 'Administration'),
        ('development', 'Development'),
        ('design', 'Design'),
        ('meetings', 'Meetings'),
        ('research', 'Research'),
        ('support', 'Support'),
        ('strategy', 'Strategy'),
        ('other', 'Other'),
    ]

    RECURRENCE_FREQ_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('days_after', 'Days After'),
        ('custom', 'Custom'),
    ]
    RECURRENCE_TRIGGER_CHOICES = [
        ('on_complete', 'When status set to Done'),
        ('on_schedule', 'On a schedule'),
    ]
    RECURRENCE_ACTION_CHOICES = [
        ('create_new', 'Create new task'),
        ('reopen', 'Reopen this task'),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='tasks')
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    assignees = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='workspace_tasks')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_workspace_tasks')
    category = models.CharField(max_length=50, blank=True, default='')
    tags = models.CharField(max_length=255, blank=True, default='')
    estimated_minutes = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Recurring task fields
    is_recurring = models.BooleanField(default=False)
    recurrence_frequency = models.CharField(max_length=20, choices=RECURRENCE_FREQ_CHOICES, blank=True, default='')
    recurrence_interval = models.PositiveIntegerField(default=1, help_text='Every X days/weeks/months/years')
    recurrence_days = models.CharField(max_length=50, blank=True, default='', help_text='Comma-separated day numbers for weekly: 0=Mon..6=Sun')
    recurrence_trigger = models.CharField(max_length=20, choices=RECURRENCE_TRIGGER_CHOICES, blank=True, default='on_complete')
    recurrence_action = models.CharField(max_length=20, choices=RECURRENCE_ACTION_CHOICES, blank=True, default='create_new')
    recur_forever = models.BooleanField(default=True)
    recurrence_count = models.PositiveIntegerField(null=True, blank=True, help_text='Repeat X times (null = forever)')
    recurrence_status_reset = models.CharField(max_length=40, blank=True, default='', help_text='Reset to this status on recurrence')
    sync_recurrence_to_due = models.BooleanField(default=True)

    def tag_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]


class Subtask(models.Model):
    STATUS_CHOICES = Task.STATUS_CHOICES
    PRIORITY_CHOICES = Task.PRIORITY_CHOICES

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=200)
    is_done = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, blank=True, default='')
    category = models.CharField(max_length=50, blank=True, default='')
    assignees = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='assigned_subtasks')
    due_date = models.DateField(null=True, blank=True)
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


CUSTOM_FIELD_TYPES = [
    ('dropdown', 'Dropdown'),
    ('labels', 'Labels'),
    ('text', 'Text'),
    ('number', 'Number'),
    ('date', 'Date'),
    ('checkbox', 'Checkbox'),
    ('url', 'URL'),
    ('email', 'Email'),
]


class CustomField(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='custom_fields')
    name = models.CharField(max_length=120)
    field_type = models.CharField(max_length=20, choices=CUSTOM_FIELD_TYPES, default='dropdown')
    visible_to_guests = models.BooleanField(default=True)
    is_private = models.BooleanField(default=False)
    is_global = models.BooleanField(default=False, help_text='Available on every list in every workspace this user can see')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='custom_fields_created')
    # Optional scoping: empty = whole workspace; otherwise restricted to selected lists
    lists = models.ManyToManyField(TaskList, blank=True, related_name='custom_fields')
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position', 'id']

    def __str__(self):
        return f"{self.name} ({self.workspace.name})"

    def location_count(self):
        c = self.lists.count()
        return c if c else self.workspace.lists.count()


class CustomFieldOption(models.Model):
    field = models.ForeignKey(CustomField, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=120)
    color = models.CharField(max_length=20, default='gray')
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position', 'id']

    def __str__(self):
        return self.name


class TaskCustomFieldValue(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='custom_values')
    field = models.ForeignKey(CustomField, on_delete=models.CASCADE, related_name='values')
    option = models.ForeignKey(CustomFieldOption, on_delete=models.SET_NULL, null=True, blank=True, related_name='task_values')
    options = models.ManyToManyField(CustomFieldOption, blank=True, related_name='task_values_multi')
    text_value = models.TextField(blank=True, default='')
    number_value = models.FloatField(null=True, blank=True)
    date_value = models.DateField(null=True, blank=True)
    bool_value = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('task', 'field')]

    def display(self):
        if self.field.field_type == 'dropdown':
            return self.option.name if self.option_id else ''
        if self.field.field_type == 'labels':
            return ', '.join(o.name for o in self.options.all())
        if self.field.field_type == 'text':
            return self.text_value
        if self.field.field_type == 'number':
            return '' if self.number_value is None else str(self.number_value)
        if self.field.field_type == 'date':
            return self.date_value.isoformat() if self.date_value else ''
        if self.field.field_type == 'checkbox':
            return 'Yes' if self.bool_value else 'No'
        return self.text_value


class CustomFieldPermission(models.Model):
    ROLE_CHOICES = [('view', 'Can view'), ('edit', 'Can edit')]
    field = models.ForeignKey(CustomField, on_delete=models.CASCADE, related_name='permissions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='custom_field_permissions')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='edit')

    class Meta:
        unique_together = [('field', 'user')]


class ViewPreference(models.Model):
    VIEW_CHOICES = [
        ('list', 'List'),
        ('board', 'Board'),
        ('calendar', 'Calendar'),
        ('gantt', 'Gantt'),
    ]
    SUBTASK_MODES = [
        ('collapsed', 'Collapsed'),
        ('expanded', 'Expanded'),
        ('separate', 'As separate tasks'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='view_preferences')
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name='view_preferences')
    view = models.CharField(max_length=20, choices=VIEW_CHOICES, default='list')

    show_empty_statuses = models.BooleanField(default=True)
    wrap_text = models.BooleanField(default=False)
    show_task_locations = models.BooleanField(default=False)
    show_subtask_parent_names = models.BooleanField(default=True)
    show_closed_tasks = models.BooleanField(default=True)
    subtasks_mode = models.CharField(max_length=20, choices=SUBTASK_MODES, default='collapsed')

    is_pinned = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    autosave_for_me = models.BooleanField(default=True)
    protected = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('user', 'task_list', 'view')]


class TimeEntry(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_entries')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='time_entries')
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    is_manual = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-started_at']

    @property
    def is_running(self):
        return self.ended_at is None and self.deleted_at is None

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def duration_seconds(self, now=None):
        from django.utils import timezone
        end = self.ended_at or (now or timezone.now())
        return max(0, int((end - self.started_at).total_seconds()))

    def __str__(self):
        return f'TimeEntry {self.pk}'


class PasswordSetupToken(models.Model):
    """Stores OTP codes for new-user password setup and password resets."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='password_tokens')
    token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def is_expired(self):
        from django.utils import timezone
        return (timezone.now() - self.created_at).total_seconds() > 86400  # 24 hours

    def __str__(self):
        return f'OTP for {self.user.username} ({self.token})'


class Notification(models.Model):
    VERB_CHOICES = [
        ('comment', 'Commented'),
        ('update', 'Updated'),
    ]
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+')
    verb = models.CharField(max_length=20, choices=VERB_CHOICES)
    description = models.CharField(max_length=255)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.actor} → {self.recipient}: {self.verb}'


class DashboardCard(models.Model):
    """User-customisable dashboard cards for the reports page."""
    WIDTH_CHOICES = [('half', 'Half'), ('full', 'Full')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dashboard_cards')
    card_type = models.CharField(max_length=40)
    position = models.IntegerField(default=0)
    width = models.CharField(max_length=10, choices=WIDTH_CHOICES, default='half')
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f'{self.user.username} – {self.card_type} @{self.position}'


class ReportTemplate(models.Model):
    """Saved filter presets for the dashboard / reports page."""
    TYPE_CHOICES = [('retainer', 'Retainer'), ('project', 'Project'), ('custom', 'Custom')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='report_templates')
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='custom')
    workspace_ids = models.JSONField(default=list, blank=True)
    list_ids = models.JSONField(default=list, blank=True)
    period = models.CharField(max_length=20, default='monthly')
    card_layout = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.user.username} – {self.name} ({self.template_type})'
