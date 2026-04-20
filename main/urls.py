# main/urls.py (app urls)
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('toggle-theme/', views.toggle_theme, name='toggle_theme'),
    path('contact/', views.contact, name='contact'),
    path('subscribe/', views.subscribe, name='subscribe'),
    
    # Authentication URLs
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analytics/', views.analytics, name='analytics'),
    path('team/', views.team, name='team'),
    path('admin-control/', views.admin_control, name='admin_control'),
    path('system-logs/', views.system_logs, name='system_logs'),

    # Project URLs
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.create_project, name='create_project'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/update/', views.update_project, name='update_project'),
    path('projects/<int:project_id>/activities/create/', views.create_activity, name='create_activity'),
    path('projects/<int:project_id>/activities/<int:activity_id>/update/', views.update_activity, name='update_activity'),
    path('projects/<int:project_id>/activities/<int:activity_id>/tasks/<int:task_id>/toggle/', views.toggle_task, name='toggle_task'),
    
    # Weekly Task URLs
    path('projects/<int:project_id>/weeks/<int:week_id>/add-task/', views.add_weekly_task, name='add_weekly_task'),
    path('projects/<int:project_id>/weeks/<int:week_id>/edit/', views.edit_project_week, name='edit_project_week'),
    path('projects/<int:project_id>/report/', views.generate_project_report, name='generate_project_report'),
    path('projects/<int:project_id>/send-report/', views.send_project_report_email, name='send_project_report_email'),
    path('projects/<int:project_id>/contact-owner/', views.contact_project_owner, name='contact_project_owner'),
    path('send-client-email/', views.send_client_email_ajax, name='send_client_email_ajax'),
    path('permission-management/', views.permission_management, name='permission_management'),
    path('user-permissions/<int:user_id>/', views.user_permissions, name='user_permissions'),
    path('projects/<int:project_id>/weekly-tasks/<int:task_id>/update/', views.update_weekly_task, name='update_weekly_task'),
    path('projects/<int:project_id>/weekly-tasks/<int:task_id>/delete/', views.delete_weekly_task, name='delete_weekly_task'),
    path('projects/<int:project_id>/weekly-tasks/<int:task_id>/details/', views.get_weekly_task_details, name='get_weekly_task_details'),
    path('projects/<int:project_id>/weekly-tasks/<int:task_id>/updates/', views.weekly_task_updates, name='weekly_task_updates'),
    path('projects/<int:project_id>/weekly-overview/', views.project_weekly_overview, name='project_weekly_overview'),
    path('projects/<int:project_id>/bulk-update-tasks/', views.bulk_update_weekly_tasks, name='bulk_update_weekly_tasks'),
    path('projects/<int:project_id>/export-weekly-tasks/', views.export_weekly_tasks, name='export_weekly_tasks'),
    path('dashboard/export-report/', views.export_project_progress_report, name='export_project_progress_report'),
    path('dashboard/export-data/', views.export_dashboard_data, name='export_dashboard_data'),
    path('dashboard/stats/', views.get_dashboard_stats, name='get_dashboard_stats'),
    path('dashboard/refresh/', views.refresh_dashboard_data, name='refresh_dashboard_data'),
    path('projects/<int:project_id>/update-status/', views.update_project_status, name='update_project_status'),
    path('client/', views.client_page, name='client_page'),

]