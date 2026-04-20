from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Project, Activity, Task, ProjectWeek, WeeklyTask, TaskUpdate, SystemLog, UserPermission

# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'can_login', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'can_login', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name', 'phone_number', 'company_name', 'position')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'can_login', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def has_delete_permission(self, request, obj=None):
        # Allow deletion of users
        return True


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'client', 'status', 'priority', 'progress', 'start_date', 'end_date', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['name', 'description', 'client', 'client_email']
    filter_horizontal = ['team']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'activity_number', 'status', 'start_date', 'end_date', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description', 'project__name']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'activity', 'completed', 'assignee', 'created_at']
    list_filter = ['completed', 'created_at']
    search_fields = ['name', 'description', 'activity__title', 'activity__project__name']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProjectWeek)
class ProjectWeekAdmin(admin.ModelAdmin):
    list_display = ['project', 'week_number', 'start_date', 'end_date', 'created_at']
    list_filter = ['created_at']
    search_fields = ['project__name']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WeeklyTask)
class WeeklyTaskAdmin(admin.ModelAdmin):
    list_display = ['project_week', 'task_name', 'status', 'progress_percentage', 'assignee', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['task_name', 'description', 'project_week__project__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TaskUpdate)
class TaskUpdateAdmin(admin.ModelAdmin):
    list_display = ['weekly_task', 'updated_by', 'new_status', 'created_at']
    list_filter = ['new_status', 'created_at']
    search_fields = ['weekly_task__task_name', 'updated_by__username', 'update_comment']
    readonly_fields = ['created_at']


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'target_model', 'target_name', 'created_at', 'ip_address']
    list_filter = ['action', 'created_at', 'target_model']
    search_fields = ['user__username', 'user__email', 'action', 'target_name']
    readonly_fields = ['created_at', 'ip_address', 'user_agent', 'session_id']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False  # System logs should only be created automatically
    
    def has_change_permission(self, request, obj=None):
        return False  # System logs should not be editable


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'permission', 'section', 'granted_at', 'granted_by', 'is_active']
    list_filter = ['permission', 'section', 'granted_at', 'is_active']
    search_fields = ['user__username', 'user__email', 'permission', 'section']
    readonly_fields = ['granted_at']
    ordering = ['-granted_at']
