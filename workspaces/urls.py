from django.urls import path

from . import views

app_name = 'workspaces'

urlpatterns = [
    path('', views.workspace_list, name='list'),
    path('create/', views.workspace_create, name='create'),
    path('<int:workspace_id>/', views.workspace_detail, name='detail'),
    path('<int:workspace_id>/delete/', views.workspace_delete, name='delete'),

    path('<int:workspace_id>/lists/create/', views.list_create, name='list_create'),
    path('lists/<int:list_id>/', views.list_detail, name='list_detail'),
    path('lists/<int:list_id>/board/', views.list_board, name='list_board'),
    path('lists/<int:list_id>/calendar/', views.list_calendar, name='list_calendar'),
    path('lists/<int:list_id>/gantt/', views.list_gantt, name='list_gantt'),
    path('lists/<int:list_id>/delete/', views.list_delete, name='list_delete'),
    path('lists/<int:list_id>/update/', views.list_update, name='list_update'),
    path('lists/<int:list_id>/statuses/create/', views.status_create, name='status_create'),
    path('statuses/<int:status_id>/delete/', views.status_delete, name='status_delete'),

    path('lists/<int:list_id>/tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/update/', views.task_update, name='task_update'),
    path('tasks/<int:task_id>/status/', views.task_update_status, name='task_update_status'),
    path('tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:task_id>/subtasks/create/', views.subtask_create, name='subtask_create'),
    path('subtasks/<int:subtask_id>/toggle/', views.subtask_toggle, name='subtask_toggle'),
    path('subtasks/<int:subtask_id>/delete/', views.subtask_delete, name='subtask_delete'),
    path('tasks/<int:task_id>/comments/create/', views.comment_create, name='comment_create'),
    path('tasks/<int:task_id>/time/start/', views.time_start, name='time_start'),
    path('tasks/<int:task_id>/time/stop/', views.time_stop, name='time_stop'),
    path('tasks/<int:task_id>/time/add/', views.time_add, name='time_add'),

    # User management (admin-only)
    path('admin/users/', views.user_list, name='user_list'),
    path('admin/users/create/', views.user_create, name='user_create'),
    path('admin/users/<int:user_id>/toggle-staff/', views.user_toggle_staff, name='user_toggle_staff'),
    path('admin/users/<int:user_id>/reset-password/', views.user_reset_password, name='user_reset_password'),
    path('admin/users/<int:user_id>/delete/', views.user_delete, name='user_delete'),

    # Workspace members
    path('<int:workspace_id>/members/', views.workspace_members, name='members'),
    path('<int:workspace_id>/members/add/', views.workspace_member_add, name='member_add'),
    path('members/<int:member_id>/update/', views.workspace_member_update, name='member_update'),
    path('members/<int:member_id>/remove/', views.workspace_member_remove, name='member_remove'),
]
