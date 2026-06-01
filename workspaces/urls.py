from django.urls import path

from . import views

app_name = 'workspaces'

urlpatterns = [
    path('', views.workspace_list, name='list'),
    path('reports/', views.reports, name='reports'),
    path('reports/cards/add/', views.dashboard_card_add, name='dashboard_card_add'),
    path('reports/cards/<int:card_id>/remove/', views.dashboard_card_remove, name='dashboard_card_remove'),
    path('reports/cards/reorder/', views.dashboard_card_reorder, name='dashboard_card_reorder'),
    path('reports/cards/<int:card_id>/resize/', views.dashboard_card_resize, name='dashboard_card_resize'),
    path('reports/cards/<int:card_id>/style/', views.dashboard_card_style, name='dashboard_card_style'),
    path('reports/cards/<int:card_id>/image/', views.dashboard_card_image, name='dashboard_card_image'),
    path('reports/cards/data/', views.dashboard_card_data, name='dashboard_card_data'),
    path('reports/preferences/', views.dashboard_pref_update, name='dashboard_pref_update'),
    path('reports/preferences/image/', views.dashboard_bg_image, name='dashboard_bg_image'),
    path('reports/templates/save/', views.report_template_save, name='report_template_save'),
    path('reports/templates/<int:template_id>/delete/', views.report_template_delete, name='report_template_delete'),
    path('settings/', views.settings_page, name='settings'),
    path('create/', views.workspace_create, name='create'),
    path('<int:workspace_id>/', views.workspace_detail, name='detail'),
    path('<int:workspace_id>/update/', views.workspace_update, name='workspace_update'),
    path('<int:workspace_id>/delete/', views.workspace_delete, name='delete'),

    path('<int:workspace_id>/categories/', views.workspace_categories, name='workspace_categories'),
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
    path('tasks/<int:task_id>/restore/', views.task_restore, name='task_restore'),
    path('tasks/<int:task_id>/subtasks/create/', views.subtask_create, name='subtask_create'),
    path('subtasks/<int:subtask_id>/toggle/', views.subtask_toggle, name='subtask_toggle'),
    path('subtasks/<int:subtask_id>/update/', views.subtask_update, name='subtask_update'),
    path('subtasks/<int:subtask_id>/delete/', views.subtask_delete, name='subtask_delete'),
    path('tasks/<int:task_id>/comments/create/', views.comment_create, name='comment_create'),
    path('tasks/<int:task_id>/time/start/', views.time_start, name='time_start'),
    path('tasks/<int:task_id>/time/stop/', views.time_stop, name='time_stop'),
    path('tasks/<int:task_id>/time/add/', views.time_add, name='time_add'),
    path('time/<int:entry_id>/delete/', views.time_entry_delete, name='time_entry_delete'),

    # Organizations (grand Workspaces)
    path('organizations/create/', views.organization_create, name='organization_create'),
    path('organizations/<int:org_id>/switch/', views.organization_switch, name='organization_switch'),

    # User management (admin-only)
    path('admin/users/', views.user_list, name='user_list'),
    path('admin/users/create/', views.user_create, name='user_create'),
    path('admin/users/<int:user_id>/toggle-staff/', views.user_toggle_staff, name='user_toggle_staff'),
    path('admin/users/<int:user_id>/set-role/', views.user_set_role, name='user_set_role'),
    path('admin/users/<int:user_id>/update/', views.user_update, name='user_update'),
    path('admin/users/<int:user_id>/reset-password/', views.user_reset_password, name='user_reset_password'),
    path('admin/users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('admin/users/<int:user_id>/allocate/', views.user_allocate_workspace, name='user_allocate'),
    path('admin/users/<int:user_id>/allocate-list/', views.user_allocate_list, name='user_allocate_list'),
    path('admin/users/<int:user_id>/send-otp/', views.user_send_otp, name='user_send_otp'),

    # OTP verification (public — no login required)
    path('otp/verify/', views.otp_verify, name='otp_verify'),

    # Custom fields
    path('<int:workspace_id>/custom-fields/', views.custom_field_manager, name='custom_field_manager'),
    path('<int:workspace_id>/custom-fields/field-<int:field_id>/', views.custom_field_manager, name='custom_field_manager_with_field'),
    path('<int:workspace_id>/custom-fields/create/', views.custom_field_create, name='custom_field_create'),
    path('<int:workspace_id>/custom-fields/quick-create/', views.custom_field_quick_create, name='custom_field_quick_create'),
    path('custom-fields/<int:field_id>/update/', views.custom_field_update, name='custom_field_update'),
    path('custom-fields/<int:field_id>/delete/', views.custom_field_delete, name='custom_field_delete'),
    path('custom-fields/<int:field_id>/options/create/', views.custom_field_option_create, name='custom_field_option_create'),
    path('custom-field-options/<int:option_id>/update/', views.custom_field_option_update, name='custom_field_option_update'),
    path('custom-field-options/<int:option_id>/delete/', views.custom_field_option_delete, name='custom_field_option_delete'),
    path('tasks/<int:task_id>/custom-fields/<int:field_id>/set/', views.task_custom_value_set, name='task_custom_value_set'),

    # View preferences
    path('lists/<int:list_id>/views/<str:view>/preferences/', views.view_preference_set, name='view_preference_set'),

    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/mark-read/', views.notification_mark_read, name='notification_mark_read'),

]
