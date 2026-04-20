from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from datetime import timedelta

class User(AbstractUser):
    """Custom user model for E-Click"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]

    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    company_name = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user', help_text="User role in the system")
    can_login = models.BooleanField(default=True, help_text="Whether this user can log in to the system")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Keep username as the login field (users login with username, not email)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']  # Email is required but username is used for login

    # Fix reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='eclick_user_set',
        related_query_name='eclick_user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='eclick_user_set',
        related_query_name='eclick_user'
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Ensure user is active by default
        if not self.pk:  # Only for new users
            self.is_active = True
        super().save(*args, **kwargs)

class Project(models.Model):
    """Project model for managing software projects"""
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('in-progress', 'In Progress'),
        ('in-progress-guidance-required', 'In Progress (Guidance Required)'),
        ('completed', 'Completed'),
        ('completed-review-pending', 'Completed (Review Pending)'),
        ('completed-data-discrepancy-addressing', 'Completed (Data Discrepancy addressing)'),
        ('on-hold', 'On Hold')
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='planning')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    progress = models.IntegerField(default=0)
    client = models.CharField(max_length=200)
    client_email = models.EmailField(blank=True, null=True, help_text="Client email for sending reports")
    team = models.ManyToManyField(User, related_name='projects')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

    def create_project_weeks(self):
        """Auto-create weeks based on project start/end dates"""
        current_date = self.start_date
        week_number = 1
        
        while current_date <= self.end_date:
            week_end = min(current_date + timedelta(days=6), self.end_date)
            
            ProjectWeek.objects.get_or_create(
                project=self,
                week_number=week_number,
                defaults={
                    'start_date': current_date,
                    'end_date': week_end
                }
            )
            
            current_date = week_end + timedelta(days=1)
            week_number += 1

    def get_current_week(self):
        """Get current week based on today's date"""
        from datetime import date
        today = date.today()
        
        return self.weeks.filter(
            start_date__lte=today,
            end_date__gte=today
        ).first()

    def get_week_progress(self):
        """Calculate overall progress based on weekly tasks"""
        total_tasks = 0
        completed_tasks = 0
        
        for week in self.weeks.all():
            week_tasks = week.tasks.all()
            total_tasks += week_tasks.count()
            completed_tasks += week_tasks.filter(status='completed').count()
        
        if total_tasks == 0:
            return 0
        return int((completed_tasks / total_tasks) * 100)

    def update_dates_from_weeks(self):
        weeks = self.weeks.all()
        if weeks.exists():
            self.start_date = weeks.order_by('start_date').first().start_date
            self.end_date = weeks.order_by('-end_date').first().end_date
            self.save(update_fields=['start_date', 'end_date'])

class ProjectWeek(models.Model):
    """Weekly breakdown for projects"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='weeks')
    week_number = models.IntegerField()  # Week 1, 2, 3, etc.
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['week_number']
        unique_together = ['project', 'week_number']
    
    def __str__(self):
        return f"{self.project.name} - Week {self.week_number}"

class WeeklyTask(models.Model):
    """Tasks for each project week"""
    STATUS_CHOICES = [
        ('not-started', 'Not Started'),
        ('in-progress', 'In Progress'),
        ('in-progress-guidance-required', 'In Progress (Guidance Required)'),
        ('progressing', 'Progressing'),
        ('completed', 'Completed'),
        ('completed-review-pending', 'Completed (Review Pending)'),
        ('completed-data-discrepancy-addressing', 'Completed (Data Discrepancy addressing)'),
        ('blocked', 'Blocked'),
        ('on-hold', 'On Hold')
    ]
    
    project_week = models.ForeignKey(ProjectWeek, on_delete=models.CASCADE, related_name='tasks')
    task_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='not-started')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='weekly_tasks')
    
    # Custom comment field
    comment = models.TextField(blank=True, help_text="Add any custom notes or updates")
    
    # Progress tracking
    progress_percentage = models.IntegerField(default=0, help_text="Progress from 0-100%")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Week {self.project_week.week_number} - {self.task_name}"

class TaskUpdate(models.Model):
    """Track updates/changes to weekly tasks"""
    weekly_task = models.ForeignKey(WeeklyTask, on_delete=models.CASCADE, related_name='updates')
    previous_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    update_comment = models.TextField(blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.weekly_task.task_name} - {self.new_status} by {self.updated_by.username}"

class SystemLog(models.Model):
    """Comprehensive logging system for all user actions"""
    ACTION_CHOICES = [
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('user_created', 'User Created'),
        ('user_updated', 'User Updated'),
        ('user_deleted', 'User Deleted'),
        ('project_created', 'Project Created'),
        ('project_updated', 'Project Updated'),
        ('project_deleted', 'Project Deleted'),
        ('task_created', 'Task Created'),
        ('task_updated', 'Task Updated'),
        ('task_deleted', 'Task Deleted'),
        ('data_export', 'Data Export'),
        ('permission_granted', 'Permission Granted'),
        ('permission_revoked', 'Permission Revoked'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='system_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    target_model = models.CharField(max_length=50, blank=True, null=True, help_text="Model that was affected")
    target_id = models.IntegerField(null=True, blank=True, help_text="ID of the affected object")
    target_name = models.CharField(max_length=200, blank=True, help_text="Name/description of the affected object")
    previous_values = models.JSONField(null=True, blank=True, help_text="Previous values before change")
    new_values = models.JSONField(null=True, blank=True, help_text="New values after change")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'System Log'
        verbose_name_plural = 'System Logs'
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"
    
    @classmethod
    def log_action(cls, user, action, target_model=None, target_id=None, target_name=None, 
                   previous_values=None, new_values=None, request=None):
        """Log an action with optional request context"""
        log_data = {
            'user': user,
            'action': action,
            'target_model': target_model,
            'target_id': target_id,
            'target_name': target_name,
            'previous_values': previous_values,
            'new_values': new_values,
        }
        
        if request:
            log_data['ip_address'] = cls.get_client_ip(request)
            log_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
            log_data['session_id'] = request.session.session_key or ''
        
        return cls.objects.create(**log_data)
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class UserPermission(models.Model):
    """Granular permission system for different application sections"""
    SECTION_CHOICES = [
        ('dashboard', 'Dashboard'),
        ('projects', 'Projects'),
        ('analytics', 'Analytics'),
        ('team', 'Team'),
        ('admin_control', 'Admin Control'),
        ('system_logs', 'System Logs'),
        ('client_emails', 'Client Emails'),
        ('project_creation', 'Project Creation'),
        ('project_editing', 'Project Editing'),
        ('task_management', 'Task Management'),
        ('report_generation', 'Report Generation'),
        ('user_management', 'User Management'),
    ]
    
    PERMISSION_CHOICES = [
        ('view', 'View'),
        ('create', 'Create'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
        ('export', 'Export'),
        ('admin', 'Admin'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permissions')
    section = models.CharField(max_length=50, choices=SECTION_CHOICES)
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='granted_permissions')
    granted_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['user', 'section', 'permission']
        verbose_name = 'User Permission'
        verbose_name_plural = 'User Permissions'
    
    def __str__(self):
        return f"{self.user.username} - {self.section} - {self.permission}"
    
    @classmethod
    def has_permission(cls, user, section, permission):
        """Check if user has specific permission for a section"""
        if user.is_superuser:
            return True
        return cls.objects.filter(
            user=user,
            section=section,
            permission=permission,
            is_active=True
        ).exists()
    
    @classmethod
    def grant_permission(cls, user, section, permission, granted_by=None):
        """Grant permission to user"""
        permission_obj, created = cls.objects.get_or_create(
            user=user,
            section=section,
            permission=permission,
            defaults={
                'granted_by': granted_by,
                'is_active': True
            }
        )
        if not created:
            permission_obj.is_active = True
            permission_obj.granted_by = granted_by
            permission_obj.save()
        return permission_obj
    
    @classmethod
    def revoke_permission(cls, user, section, permission):
        """Revoke permission from user"""
        try:
            permission_obj = cls.objects.get(
                user=user,
                section=section,
                permission=permission
            )
            permission_obj.is_active = False
            permission_obj.save()
            return True
        except cls.DoesNotExist:
            return False

class Activity(models.Model):
    """Activity model for project tasks"""
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('in-progress', 'In Progress'),
        ('in-progress-guidance-required', 'In Progress (Guidance Required)'),
        ('completed', 'Completed'),
        ('completed-review-pending', 'Completed (Review Pending)'),
        ('completed-data-discrepancy-addressing', 'Completed (Data Discrepancy addressing)'),
        ('blocked', 'Blocked')
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='activities')
    activity_number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='planning')
    progress = models.IntegerField(default=0)
    can_start_independently = models.BooleanField(default=True)
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='dependent_activities')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['activity_number']
        unique_together = ['project', 'activity_number']
    
    def __str__(self):
        return f"{self.project.name} - Activity {self.activity_number}: {self.title}"

class Task(models.Model):
    """Task model for activity items"""
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='main_assigned_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.activity.title} - {self.name}"