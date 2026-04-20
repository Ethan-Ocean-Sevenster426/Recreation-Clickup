# main/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse

from django.views.decorators.http import require_POST
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.backends import ModelBackend
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import User, Project, Activity, Task, ProjectWeek, WeeklyTask, TaskUpdate, SystemLog, UserPermission
from .forms import ProjectForm, ActivityForm, TaskForm
import json
import csv
from datetime import datetime, timedelta
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Circle, Wedge, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
from reportlab.platypus.flowables import Flowable
import math


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Project




def require_permission(section, permission):
    """Decorator to check if user has specific permission"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('main:login')
            
            if not UserPermission.has_permission(request.user, section, permission):
                messages.error(request, f'You do not have {permission} permission for {section}.')
                return redirect('main:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


class EmailBackend(ModelBackend):
    """Custom authentication backend to login with email"""
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        try:
            # Try to find user by email
            user = User.objects.get(email=email or username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        return None

def home(request):
    """Home page view with all sections"""
    
    # Data for different sections
    context = {
        'testimonials': [
            {
                'name': 'Jennifer Smith',
                'role': 'CTO, TechCorp Inc.',
                'message': "E-click transformed our business operations by implementing their custom ERP solution. We've seen a 30% increase in productivity and significant cost savings.",
                'rating': 5,
                'initials': 'JS'
            },
            {
                'name': 'Michael Johnson',
                'role': 'CEO, Startup Ventures',
                'message': 'As a startup, we needed a flexible solution that could grow with us. E-click delivered an outstanding platform that has been instrumental in our rapid growth.',
                'rating': 5,
                'initials': 'MJ'
            },
            {
                'name': 'Sarah Williams',
                'role': 'Operations Director, Global Retail',
                'message': 'The e-commerce platform developed by E-click has completely revolutionized our online presence. Our sales have increased by 45% since implementation.',
                'rating': 4,
                'initials': 'SW'
            },
            {
                'name': 'Robert Chen',
                'role': 'IT Manager, Healthcare Solutions',
                'message': "E-click's attention to detail and understanding of our industry's compliance requirements made them the perfect partner for our digital transformation journey.",
                'rating': 5,
                'initials': 'RC'
            }
        ],
        'companies': [
            {
                'name': 'FSA',
                'logo_url': 'images/FSA LOGO.png',
                'alt': 'FSA logo'
            },
            {
                'name': 'NAB',
                'logo_url': 'images/NAB Logo.jpg',
                'alt': 'NAB logo'
            },
            {
                'name': 'Prokon',
                'logo_url': 'images/Prokon Logo.png',
                'alt': 'Prokon logo'
            }
        ],
        'services': [
            {
                'title': 'Custom Software Development',
                'description': 'Tailor-made software solutions designed to meet your specific business requirements and challenges.',
                'icon': 'code'
            },
            {
                'title': 'Cloud-Based Solutions', 
                'description': 'Scalable and secure cloud infrastructure that grows with your business needs and reduces IT costs.',
                'icon': 'database'
            },
            {
                'title': 'Business Process Automation',
                'description': 'Streamline your operations with intelligent automation solutions that reduce manual tasks and increase efficiency.',
                'icon': 'zap'
            },
            {
                'title': 'Enterprise Integration',
                'description': 'Seamless integration of your existing systems with modern software solutions for improved efficiency.',
                'icon': 'server'
            },
            {
                'title': 'Technical Consultancy',
                'description': 'Expert advice and strategic planning to optimize your technology investments and digital transformation.',
                'icon': 'settings'
            }
        ],
        'solutions': [
            {
                'id': 'enterprise',
                'title': 'Enterprise Solutions',
                'description': 'Powerful infrastructure for large organizations with complex requirements.',
                'features': [
                    'ERP Integration',
                    'Workflow Automation', 
                    'Business Analytics',
                    'Multi-department Collaboration'
                ]
            },
            {
                'id': 'smb',
                'title': 'Small Business Solutions',
                'description': 'Affordable software that scales with your small to medium business.',
                'features': [
                    'CRM Systems',
                    'Payment Solutions',
                    'Marketing Automation',
                    'Cloud Storage'
                ]
            },
            {
                'id': 'startup',
                'title': 'Startup Innovation',
                'description': 'Agile solutions for startups looking to disrupt their industries.',
                'features': [
                    'MVP Development',
                    'Rapid Prototyping',
                    'API Integration',
                    'Scalable Architecture'
                ]
            }
        ]
    }
    
    return render(request, 'home.html', context)

@require_POST
def toggle_theme(request):
    """Toggle between light and dark theme"""
    current_theme = request.session.get('theme', 'light')
    new_theme = 'dark' if current_theme == 'light' else 'light'
    request.session['theme'] = new_theme
    
    return JsonResponse({'theme': new_theme})

def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Validation
        if not all([first_name, last_name, email, subject, message]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'contact.html')
        
        if not email or '@' not in email:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'contact.html')
        
        try:
            # Import email service
            from home.email_service import email_service
            
            # Create email content
            full_name = f"{first_name} {last_name}"
            email_subject = f"Contact Form: {subject}"
            
            # Create HTML email body - Simple and professional
            html_body = f"""<html>
<body style="font-family: Arial, sans-serif;">
    <p><strong>New Contact Form Submission - E-Click Website</strong></p>

    <p><strong>Name:</strong> {full_name}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>Phone:</strong> {phone if phone else 'Not provided'}</p>
    <p><strong>Subject:</strong> {subject}</p>

    <p><strong>Message:</strong></p>
    <p>{message}</p>

    <hr>
    <p><strong>Submission Details:</strong></p>
    <p>Submitted on: {request.META.get('HTTP_HOST', 'Unknown')}</p>
    <p>IP Address: {request.META.get('REMOTE_ADDR', 'Unknown')}</p>
    <p>User Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}</p>

    <p>Best regards,<br>E-Click Contact Form System</p>
</body>
</html>"""

            # Create user confirmation email - Simple and professional
            user_confirmation_html = f"""<html>
<body style="font-family: Arial, sans-serif;">
    <p>Dear {full_name},</p>

    <p>Thank you for contacting E-Click. We have received your message and will respond to you as soon as possible.</p>

    <p><strong>Your message details:</strong></p>
    <p><strong>Subject:</strong> {subject}</p>
    <p><strong>Message:</strong> {message}</p>

    <p><strong>Need immediate assistance?</strong></p>
    <p>Phone: +27 76 740 1777<br>
    Email: info@eclick.co.za<br>
    Office Hours: Monday - Friday: 8:00 AM - 6:00 PM SAST</p>

    <p>Best regards,<br>E-Click Project Management Team</p>
</body>
</html>"""
            
            # Create plain text version
            text_body = f"""
New Contact Form Submission - E-Click Website

Name: {full_name}
Email: {email}
Phone: {phone if phone else 'Not provided'}
Subject: {subject}

Message:
{message}

---
Submitted on: {request.META.get('HTTP_HOST', 'Unknown')}
IP Address: {request.META.get('REMOTE_ADDR', 'Unknown')}
            """
            
            # Send email to admin
            admin_email_result = email_service.send_email(
                to_email='info@eclick.co.za',
                subject=email_subject,
                body=html_body,
                from_email=email_service.from_email,
                cc_emails=['admin@eclick.co.za']  # CC to admin for monitoring
            )

            # Send confirmation email to user
            user_email_result = email_service.send_email(
                to_email=email,
                subject="Thank you for contacting E-Click - We've received your message",
                body=user_confirmation_html,
                from_email=email_service.from_email,
                cc_emails=['admin@eclick.co.za']  # CC to admin for monitoring
            )
            
            # Check if both emails were sent successfully
            if admin_email_result['success'] and user_email_result['success']:
                messages.success(request, 'Thank you! Your message has been sent successfully. We\'ll get back to you soon, and you\'ll receive a confirmation email.')
            elif admin_email_result['success']:
                messages.warning(request, 'Your message was received by our team, but we couldn\'t send you a confirmation email. We\'ll still get back to you soon.')
            elif user_email_result['success']:
                messages.warning(request, 'You\'ll receive a confirmation email, but there was an issue sending your message to our team. Please try again or contact us directly.')
            else:
                messages.error(request, 'Sorry, there was an error sending your message. Please try again or contact us directly at +27 76 740 1777.')
                return render(request, 'contact.html')
            
            # Log the contact form submission
            try:
                from home.models import SystemLog
                SystemLog.log_action(
                    user=None,
                    action='contact_form_submission',
                    target_model='Contact',
                    target_id=None,
                    target_name=f"Contact from {full_name} ({email})",
                    request=request
                )
            except Exception as log_error:
                # Log error but don't fail the form submission
                print(f"Failed to log contact form submission: {log_error}")
            
            # Redirect to prevent form resubmission
            return redirect('main:contact')
            
        except Exception as e:
            print(f"Contact form error: {str(e)}")
            messages.error(request, f'Sorry, there was an error sending your message: {str(e)}. Please try again or contact us directly at +27 76 740 1777.')
            return render(request, 'contact.html')
    
    return render(request, 'contact.html')

@require_POST 
def subscribe(request):
    """Newsletter subscription endpoint"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        # Here you would typically save to database or send to email service
        # For now, just return success
        
        return JsonResponse({
            'status': 'success',
            'message': 'Thank you for subscribing!'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': 'Failed to subscribe. Please try again.'
        }, status=400)

def signup(request):
    """User registration view - FIXED"""
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        company_name = request.POST.get('company_name', '')
        position = request.POST.get('position', '')
        phone_number = request.POST.get('phone_number', '')

        # Validation
        if not email or not username or not password:
            messages.error(request, 'Email, username, and password are required')
            return render(request, 'auth/signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'auth/signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'auth/signup.html')

        try:
            # Create user
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
                company_name=company_name,
                position=position,
                phone_number=phone_number
            )
            
            # Log the user in immediately after signup
            user.backend = 'main.backends.EmailBackend'
            login(request, user)
            messages.success(request, 'Account created successfully!')
            print(f"User {user.email} logged in successfully, is_authenticated: {user.is_authenticated}")
            return redirect('main:dashboard')
            
        except Exception as e:
            print(f"Signup error: {str(e)}")
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'auth/signup.html')

    return render(request, 'auth/signup.html')

def login_view(request):
    """Simplified user login view without CSRF"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Email and password are required')
            return render(request, 'auth/login.html')
        
        try:
            # Find user by email
            user = User.objects.get(email=email)
            
            # Check if user can login
            if not user.can_login:
                messages.error(request, 'Access denied. Your account has been disabled.')
                return render(request, 'auth/login.html')
            
            # Check password
            if user.check_password(password):
                user.backend = 'main.backends.EmailBackend'
                login(request, user)
                messages.success(request, 'Logged in successfully!')
                
                # Redirect to next page if specified, otherwise dashboard
                next_page = request.GET.get('next', 'main:dashboard')
                return redirect(next_page)
            else:
                messages.error(request, 'Invalid email or password')
                
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
        except Exception as e:
            messages.error(request, 'An error occurred. Please try again.')
            
        return render(request, 'auth/login.html')

    return render(request, 'auth/login.html')

@login_required
def logout_view(request):
    """User logout view"""
    # Log logout before actually logging out
    SystemLog.log_action(
        user=request.user,
        action='user_logout',
        target_model='User',
        target_name=f"User logged out from {request.META.get('REMOTE_ADDR', 'Unknown IP')}",
        request=request
    )
    
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('main:home')

@login_required
def dashboard(request):
    """Enhanced dashboard view with proper data serialization"""
    print(f"Dashboard accessed by user: {request.user}, is_authenticated: {request.user.is_authenticated}")
    
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to access the dashboard.')
        return redirect('main:login')
    
    # Get projects - all projects for admins, team projects for regular users
    if request.user.is_superuser:
        # Admins see all projects (shared)
        projects = Project.objects.all().select_related('created_by').prefetch_related('weeks__tasks', 'activities', 'team')
    else:
        # Regular users see only their team projects
        projects = Project.objects.filter(team=request.user).select_related('created_by').prefetch_related('weeks__tasks', 'activities', 'team')
    
    # Calculate project statistics
    total_projects = projects.count()
    in_progress = projects.filter(status='in-progress').count()
    completed = projects.filter(status='completed').count()
    planning = projects.filter(status='planning').count()
    
    # Get recent activities from all projects
    recent_activities = Activity.objects.filter(
        project__in=projects
    ).select_related('project').order_by('-created_at')[:10]
    
    # Serialize projects data for JavaScript
    projects_data = []
    for project in projects:
        # Get project weeks with tasks
        weeks_data = []
        for week in project.weeks.all():
            week_tasks = week.tasks.all()
            weeks_data.append({
                'id': week.id,
                'week_number': week.week_number,
                'start_date': week.start_date.isoformat() if week.start_date else None,
                'end_date': week.end_date.isoformat() if week.end_date else None,
                'total_tasks': week_tasks.count(),
                'completed_tasks': week_tasks.filter(status='completed').count(),
                'in_progress_tasks': week_tasks.filter(status__in=['in-progress', 'progressing']).count(),
                'status': 'completed' if week_tasks.count() > 0 and week_tasks.filter(status='completed').count() == week_tasks.count() else 'in-progress' if week_tasks.filter(status__in=['in-progress', 'progressing']).count() > 0 else 'pending'
            })
        
        # Calculate project progress based on activities and weekly tasks
        total_activities = project.activities.count()
        completed_activities = project.activities.filter(status='completed').count()
        activity_progress = (completed_activities / total_activities * 100) if total_activities > 0 else 0
        
        total_weekly_tasks = sum(week['total_tasks'] for week in weeks_data)
        completed_weekly_tasks = sum(week['completed_tasks'] for week in weeks_data)
        weekly_progress = (completed_weekly_tasks / total_weekly_tasks * 100) if total_weekly_tasks > 0 else 0
        
        # Use the higher of the two progress calculations
        calculated_progress = max(activity_progress, weekly_progress)
        
        projects_data.append({
            'id': project.id,
            'name': project.name,
            'client': getattr(project, 'client', 'Unknown Client'),
            'status': project.status,
            'progress': int(calculated_progress),
            'start_date': project.start_date.isoformat() if project.start_date else None,
            'end_date': project.end_date.isoformat() if project.end_date else None,
            'created_by': project.created_by.username if project.created_by else 'Unknown',
            'team_count': project.team.count(),
            'priority': getattr(project, 'priority', 'Medium'),
            'risk_level': getattr(project, 'risk_level', 'Low'),
            'budget_status': getattr(project, 'budget_status', 'On Track'),
            'weeks': weeks_data,
            'activities': [{
                'id': activity.id,
                'name': activity.name,
                'status': activity.status,
                'progress': getattr(activity, 'progress', 0)
            } for activity in project.activities.all()]
        })
    
    # Serialize activities data for JavaScript
    activities_data = []
    for activity in recent_activities:
        activities_data.append({
            'id': activity.id,
            'title': activity.name,
            'project': activity.project.name,
            'project_id': activity.project.id,
            'status': activity.status,
            'type': getattr(activity, 'activity_type', 'update'),
            'created_at': activity.created_at.isoformat(),
            'updated_at': activity.updated_at.isoformat() if hasattr(activity, 'updated_at') else activity.created_at.isoformat()
        })
    
    context = {
        'total_projects': total_projects,
        'in_progress': in_progress,
        'completed': completed,
        'planning': planning,
        'projects': projects,
        'recent_activities': recent_activities,
        'projects_json': json.dumps(projects_data, cls=DjangoJSONEncoder),
        'activities_json': json.dumps(activities_data, cls=DjangoJSONEncoder),
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def project_list(request):
    """View for listing all projects"""
    projects = Project.objects.filter(team=request.user).order_by('-start_date')
    return render(request, 'projects/project_list.html', {'projects': projects})

@login_required
@require_permission('project_creation', 'create')
def create_project(request):
    """View for creating a new project - Admin only"""
    # Check if user is admin
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Only administrators can create projects.')
        return redirect('main:dashboard')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            # Don't set start_date and end_date here - they'll be set when weeks are added
            project.save()
            
            # Add all admins to the team (shared projects)
            admin_users = User.objects.filter(is_superuser=True)
            project.team.add(*admin_users)
            form.save_m2m()  # Save many-to-many relationships
            
            # Log project creation
            SystemLog.log_action(
                user=request.user,
                action='project_created',
                target_model='Project',
                target_id=project.id,
                target_name=project.name,
                new_values={
                    'name': project.name,
                    'description': project.description,
                    'status': project.status,
                    'priority': project.priority,
                    'client': project.client
                },
                request=request
            )
            
            messages.success(request, 'Project created successfully! You can now add weeks to set the project timeline.')
            return redirect('main:project_detail', project_id=project.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm()
    return render(request, 'projects/project_form.html', {'form': form, 'action': 'Create'})

@login_required
def project_detail(request, project_id):
    """View for project details and Gantt chart"""
    from datetime import date, timedelta  # Ensure timedelta is available
    project = get_object_or_404(Project, id=project_id, team=request.user)
    
    # Ensure weeks are created for the project
    if not project.weeks.exists():
        # If no weeks exist, create a default week
        today = date.today()
        week = ProjectWeek.objects.create(
            project=project,
            week_number=1,
            start_date=today,
            end_date=today + timedelta(days=6)
        )
        # Update project dates from the new week
        project.update_dates_from_weeks()
    
    # Get all weeks with their tasks
    weeks = project.weeks.prefetch_related('tasks__assignee').all()
    current_week = project.get_current_week()
    
    # Generate list of weeks for the Gantt chart
    if project.start_date and project.end_date:
        start_date = project.start_date
        end_date = project.end_date
        gantt_weeks = []
        current_date = start_date
        while current_date <= end_date:
            gantt_weeks.append(current_date)
            current_date += timedelta(days=7)
    else:
        gantt_weeks = []
    
    # Calculate activity statistics
    total_activities = project.activities.count()
    completed_activities = project.activities.filter(status='completed').count()
    in_progress_activities = project.activities.filter(status='in-progress').count()
    planning_activities = project.activities.filter(status='planning').count()
    
    # Calculate weekly task statistics
    total_weekly_tasks = WeeklyTask.objects.filter(project_week__project=project).count()
    completed_weekly_tasks = WeeklyTask.objects.filter(project_week__project=project, status='completed').count()
    
    context = {
        'project': project,
        'weeks': weeks,
        'current_week': current_week,
        'gantt_weeks': gantt_weeks,
        'total_activities': total_activities,
        'completed_activities': completed_activities,
        'in_progress_activities': in_progress_activities,
        'planning_activities': planning_activities,
        'total_weekly_tasks': total_weekly_tasks,
        'completed_weekly_tasks': completed_weekly_tasks,
    }
    return render(request, 'projects/project_detail.html', context)

@login_required
def update_project(request, project_id):
    """View for updating a project"""
    project = get_object_or_404(Project, id=project_id, team=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            # After updating, update project dates from weeks
            project.update_dates_from_weeks()
            messages.success(request, 'Project updated successfully!')
            return redirect('main:project_detail', project_id=project.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form, 'action': 'Update'})

@login_required
def create_activity(request, project_id):
    """View for creating a new activity"""
    project = get_object_or_404(Project, id=project_id, team=request.user)
    if request.method == 'POST':
        print("POST data:", request.POST)  # Debug print
        form = ActivityForm(request.POST, project=project)
        print("Form is valid:", form.is_valid())  # Debug print
        if form.is_valid():
            try:
                activity = form.save(commit=False)
                activity.project = project
                activity.activity_number = project.activities.count() + 1
                activity.save()
                print("Activity saved successfully:", activity.id)  # Debug print
                messages.success(request, 'Activity created successfully!')
                return redirect('main:project_detail', project_id=project.id)
            except Exception as e:
                print("Error saving activity:", str(e))  # Debug print
                messages.error(request, f'Error creating activity: {str(e)}')
        else:
            print("Form errors:", form.errors)  # Debug print
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ActivityForm(project=project)
    
    context = {
        'form': form,
        'project': project,
        'action': 'Create'
    }
    print("Rendering form with context:", context)  # Debug print
    return render(request, 'projects/activity_form.html', context)

@login_required
def update_activity(request, project_id, activity_id):
    """View for updating an activity"""
    project = get_object_or_404(Project, id=project_id, team=request.user)
    activity = get_object_or_404(Activity, id=activity_id, project=project)
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Activity updated successfully!')
            return redirect('main:project_detail', project_id=project.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ActivityForm(instance=activity, project=project)
    return render(request, 'projects/activity_form.html', {'form': form, 'project': project, 'action': 'Update'})

@login_required
def toggle_task(request, project_id, activity_id, task_id):
    """View for toggling task completion status"""
    project = get_object_or_404(Project, id=project_id, team=request.user)
    activity = get_object_or_404(Activity, id=activity_id, project=project)
    task = get_object_or_404(Task, id=task_id, activity=activity)
    
    task.completed = not task.completed
    task.save()
    
    # Update activity progress
    total_tasks = activity.tasks.count()
    completed_tasks = activity.tasks.filter(completed=True).count()
    activity.progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
    activity.status = 'completed' if activity.progress == 100 else 'in-progress' if activity.progress > 0 else 'planning'
    activity.save()
    
    # Update project progress
    total_activities = project.activities.count()
    completed_activities = project.activities.filter(status='completed').count()
    project.progress = int((completed_activities / total_activities) * 100) if total_activities > 0 else 0
    project.status = 'completed' if project.progress == 100 else 'in-progress' if project.progress > 0 else 'planning'
    project.save()
    
    return JsonResponse({
        'task_completed': task.completed,
        'activity_progress': activity.progress,
        'activity_status': activity.status,
        'project_progress': project.progress,
        'project_status': project.status
    })

# New Weekly Task Views

@login_required
def add_weekly_task(request, project_id, week_id):
    """Add a new task to a specific week"""
    project = get_object_or_404(Project, id=project_id, team=request.user)
    week = get_object_or_404(ProjectWeek, id=week_id, project=project)
    
    if request.method == 'POST':
        task_name = request.POST.get('task_name')
        description = request.POST.get('description', '')
        status = request.POST.get('status', 'not-started')
        assignee_id = request.POST.get('assignee')
        comment = request.POST.get('comment', '')
        
        if task_name:
            task = WeeklyTask.objects.create(
                project_week=week,
                task_name=task_name,
                description=description,
                status=status,
                assignee_id=assignee_id if assignee_id else None,
                comment=comment
            )
            
            # Log task creation
            SystemLog.log_action(
                user=request.user,
                action='task_created',
                target_model='WeeklyTask',
                target_id=task.id,
                target_name=f"{task.task_name} (Week {week.week_number})",
                new_values={
                    'task_name': task.task_name,
                    'description': task.description,
                    'status': task.status,
                    'project': project.name,
                    'week_number': week.week_number
                },
                request=request
            )
            
            messages.success(request, f'Task "{task_name}" added to Week {week.week_number}')
            # Update project dates after adding a task (in case weeks are added/edited)
            project.update_dates_from_weeks()
        else:
            messages.error(request, 'Task name is required')
    
    return redirect('main:project_detail', project_id=project.id)

@login_required
def update_weekly_task(request, project_id, task_id):
    """Update a weekly task"""
    project = get_object_or_404(Project, id=project_id, team=request.user)
    task = get_object_or_404(WeeklyTask, id=task_id, project_week__project=project)
    
    if request.method == 'POST':
        previous_status = task.status
        
        task.task_name = request.POST.get('task_name', task.task_name)
        task.description = request.POST.get('description', task.description)
        task.status = request.POST.get('status', task.status)
        task.comment = request.POST.get('comment', task.comment)
        task.progress_percentage = int(request.POST.get('progress_percentage', task.progress_percentage))
        
        assignee_id = request.POST.get('assignee')
        if assignee_id:
            task.assignee_id = assignee_id
        
        task.save()
        
        # Log task update
        SystemLog.log_action(
            user=request.user,
            action='task_updated',
            target_model='WeeklyTask',
            target_id=task.id,
            target_name=f"{task.task_name} (Week {task.project_week.week_number})",
            previous_values={'status': previous_status},
            new_values={
                'task_name': task.task_name,
                'status': task.status,
                'progress_percentage': task.progress_percentage,
                'comment': task.comment
            },
            request=request
        )
        
        # Create task update record if status changed
        if previous_status != task.status:
            TaskUpdate.objects.create(
                weekly_task=task,
                previous_status=previous_status,
                new_status=task.status,
                update_comment=request.POST.get('update_comment', ''),
                updated_by=request.user
            )
        
        messages.success(request, f'Task "{task.task_name}" updated successfully')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'task_name': task.task_name,
                'status': task.status,
                'progress': task.progress_percentage,
                'comment': task.comment
            })
    
    return redirect('main:project_detail', project_id=project.id)

@login_required
def edit_project_week(request, project_id, week_id):
    """Edit a project week to change date range"""
    project = get_object_or_404(Project, id=project_id, team=request.user)
    week = get_object_or_404(ProjectWeek, id=week_id, project=project)
    
    if request.method == 'POST':
        from .forms import ProjectWeekForm
        form = ProjectWeekForm(request.POST, instance=week)
        if form.is_valid():
            form.save()
            # Update project dates after editing week
            project.update_dates_from_weeks()
            messages.success(request, f'Week {week.week_number} updated successfully')
            return redirect('main:project_detail', project_id=project.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        from .forms import ProjectWeekForm
        form = ProjectWeekForm(instance=week)
    
    context = {
        'form': form,
        'project': project,
        'week': week,
        'action': 'Edit'
    }
    return render(request, 'projects/week_form.html', context)

@login_required
def delete_weekly_task(request, project_id, task_id):
    """Delete a weekly task"""
    project = get_object_or_404(Project, id=project_id, team=request.user)
    task = get_object_or_404(WeeklyTask, id=task_id, project_week__project=project)
    
    task_name = task.task_name
    week_number = task.project_week.week_number
    
    # Log task deletion before deleting
    SystemLog.log_action(
        user=request.user,
        action='task_deleted',
        target_model='WeeklyTask',
        target_id=task.id,
        target_name=f"{task_name} (Week {week_number})",
        previous_values={
            'task_name': task.task_name,
            'status': task.status,
            'description': task.description,
            'project': project.name,
            'week_number': week_number
        },
        request=request
    )
    
    task.delete()
    # Update project dates after deleting a week/task
    project.update_dates_from_weeks()
    
    messages.success(request, f'Task "{task_name}" deleted successfully')
    return redirect('main:project_detail', project_id=project.id)

@login_required
def get_weekly_task_details(request, project_id, task_id):
    """Get weekly task details via AJAX"""
    project = get_object_or_404(Project, id=project_id, team=request.user)
    task = get_object_or_404(WeeklyTask, id=task_id, project_week__project=project)
    
    data = {
        'id': task.id,
        'task_name': task.task_name,
        'description': task.description,
        'status': task.status,
        'progress_percentage': task.progress_percentage,
        'comment': task.comment,
        'assignee_id': task.assignee.id if task.assignee else None,
        'assignee_name': task.assignee.username if task.assignee else None,
        'week_number': task.project_week.week_number,
        'created_at': task.created_at.strftime('%Y-%m-%d %H:%M'),
        'updated_at': task.updated_at.strftime('%Y-%m-%d %H:%M')
    }
    
    return JsonResponse(data)

@login_required
def weekly_task_updates(request, project_id, task_id):
    """Get task update history"""
    project = get_object_or_404(Project, id=project_id, team=request.user)
    task = get_object_or_404(WeeklyTask, id=task_id, project_week__project=project)
    
    updates = task.updates.select_related('updated_by').all()
    
    data = []
    for update in updates:
        data.append({
            'previous_status': update.previous_status,
            'new_status': update.new_status,
            'comment': update.update_comment,
            'updated_by': update.updated_by.username,
            'created_at': update.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({'updates': data})

@login_required
def project_weekly_overview(request, project_id):
    """Get weekly overview for a project"""
    project = get_object_or_404(Project, id=project_id, team=request.user)
    
    weeks_data = []
    for week in project.weeks.all():
        tasks = week.tasks.all()
        weeks_data.append({
            'week_number': week.week_number,
            'start_date': week.start_date.strftime('%Y-%m-%d'),
            'end_date': week.end_date.strftime('%Y-%m-%d'),
            'total_tasks': tasks.count(),
            'completed_tasks': tasks.filter(status='completed').count(),
            'in_progress_tasks': tasks.filter(status__in=['in-progress', 'progressing']).count(),
            'not_started_tasks': tasks.filter(status='not-started').count(),
            'blocked_tasks': tasks.filter(status='blocked').count(),
        })
    
    return JsonResponse({
        'project_name': project.name,
        'weeks': weeks_data
    })

@login_required
def bulk_update_weekly_tasks(request, project_id):
    """Bulk update multiple weekly tasks"""
    project = get_object_or_404(Project, id=project_id, team=request.user)
    
    if request.method == 'POST':
        task_updates = json.loads(request.body)
        updated_count = 0
        
        for task_data in task_updates:
            try:
                task = WeeklyTask.objects.get(
                    id=task_data['task_id'],
                    project_week__project=project
                )
                
                previous_status = task.status
                
                # Update fields if provided
                if 'status' in task_data:
                    task.status = task_data['status']
                if 'progress_percentage' in task_data:
                    task.progress_percentage = task_data['progress_percentage']
                if 'comment' in task_data:
                    task.comment = task_data['comment']
                if 'assignee_id' in task_data:
                    task.assignee_id = task_data['assignee_id'] if task_data['assignee_id'] else None
                
                task.save()
                
                # Create update record if status changed
                if previous_status != task.status:
                    TaskUpdate.objects.create(
                        weekly_task=task,
                        previous_status=previous_status,
                        new_status=task.status,
                        update_comment=task_data.get('update_comment', ''),
                        updated_by=request.user
                    )
                
                updated_count += 1
                
            except WeeklyTask.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'updated_count': updated_count,
            'message': f'{updated_count} tasks updated successfully'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})
@login_required
def export_weekly_tasks(request, project_id):
   """Export weekly tasks to CSV"""
   project = get_object_or_404(Project, id=project_id, team=request.user)
   
   response = HttpResponse(content_type='text/csv')
   response['Content-Disposition'] = f'attachment; filename="{project.name}_weekly_tasks.csv"'
   
   writer = csv.writer(response)
   writer.writerow([
       'Week Number', 'Week Start', 'Week End', 'Task Name', 'Description', 
       'Status', 'Progress %', 'Assignee', 'Comment', 'Created', 'Updated'
   ])
   
   for week in project.weeks.all():
       for task in week.tasks.all():
           writer.writerow([
               week.week_number,
               week.start_date,
               week.end_date,
               task.task_name,
               task.description,
               task.get_status_display(),
               task.progress_percentage,
               task.assignee.username if task.assignee else '',
               task.comment,
               task.created_at.strftime('%Y-%m-%d %H:%M'),
               task.updated_at.strftime('%Y-%m-%d %H:%M')
           ])
   
   return response

# New Export Views for Dashboard

@login_required
def export_project_progress_report(request):
   """Export detailed project progress report"""
   projects = Project.objects.filter(team=request.user).select_related('created_by').prefetch_related('weeks__tasks', 'activities', 'team')
   
   response = HttpResponse(content_type='text/csv')
   response['Content-Disposition'] = 'attachment; filename="project_progress_report.csv"'
   
   writer = csv.writer(response)
   
   # Header row
   writer.writerow([
       'Project Name', 'Client', 'Status', 'Progress %', 'Start Date', 'End Date', 
       'Duration (Days)', 'Total Activities', 'Completed Activities', 
       'Total Weekly Tasks', 'Completed Weekly Tasks', 'Current Week', 
       'Team Members', 'Created By', 'Priority', 'Risk Level', 'Budget Status',
       'Created Date', 'Last Updated'
   ])
   
   for project in projects:
       # Calculate metrics
       total_activities = project.activities.count()
       completed_activities = project.activities.filter(status='completed').count()
       
       weeks = project.weeks.all()
       total_weekly_tasks = sum(week.tasks.count() for week in weeks)
       completed_weekly_tasks = sum(week.tasks.filter(status='completed').count() for week in weeks)
       
       # Find current week
       today = datetime.now().date()
       current_week = None
       for week in weeks:
           if week.start_date <= today <= week.end_date:
               current_week = f"Week {week.week_number}"
               break
       
       # Calculate duration
       duration = (project.end_date - project.start_date).days if project.start_date and project.end_date else 0
       
       # Calculate progress
       activity_progress = (completed_activities / total_activities * 100) if total_activities > 0 else 0
       weekly_progress = (completed_weekly_tasks / total_weekly_tasks * 100) if total_weekly_tasks > 0 else 0
       overall_progress = max(activity_progress, weekly_progress)
       
       writer.writerow([
           project.name,
           getattr(project, 'client_name', 'Unknown Client'),
           project.status.title(),
           f"{overall_progress:.1f}%",
           project.start_date.strftime('%Y-%m-%d') if project.start_date else 'N/A',
           project.end_date.strftime('%Y-%m-%d') if project.end_date else 'N/A',
           duration,
           total_activities,
           completed_activities,
           total_weekly_tasks,
           completed_weekly_tasks,
           current_week or 'N/A',
           project.team.count(),
           project.created_by.username if project.created_by else 'Unknown',
           getattr(project, 'priority', 'Medium'),
           getattr(project, 'risk_level', 'Low'),
           getattr(project, 'budget_status', 'On Track'),
           project.created_at.strftime('%Y-%m-%d %H:%M') if hasattr(project, 'created_at') else 'N/A',
           project.updated_at.strftime('%Y-%m-%d %H:%M') if hasattr(project, 'updated_at') else 'N/A'
       ])
   
   return response

@login_required
def export_dashboard_data(request):
   """Export dashboard data as JSON for external tools"""
   projects = Project.objects.filter(team=request.user).select_related('created_by').prefetch_related('weeks__tasks', 'activities', 'team')
   
   data = {
       'export_date': datetime.now().isoformat(),
       'user': request.user.username,
       'summary': {
           'total_projects': projects.count(),
           'in_progress': projects.filter(status='in-progress').count(),
           'completed': projects.filter(status='completed').count(),
           'planning': projects.filter(status='planning').count(),
       },
       'projects': []
   }
   
   for project in projects:
       weeks_data = []
       for week in project.weeks.all():
           week_tasks = week.tasks.all()
           weeks_data.append({
               'week_number': week.week_number,
               'start_date': week.start_date.isoformat() if week.start_date else None,
               'end_date': week.end_date.isoformat() if week.end_date else None,
               'tasks': [{
                   'id': task.id,
                   'name': task.task_name,
                   'status': task.status,
                   'progress': task.progress_percentage,
                   'assignee': task.assignee.username if task.assignee else None
               } for task in week_tasks]
           })
       
       project_data = {
           'id': project.id,
           'name': project.name,
           'status': project.status,
           'start_date': project.start_date.isoformat() if project.start_date else None,
           'end_date': project.end_date.isoformat() if project.end_date else None,
           'team_members': [member.username for member in project.team.all()],
           'weeks': weeks_data,
           'activities': [{
               'id': activity.id,
               'name': activity.name,
               'status': activity.status,
               'created_at': activity.created_at.isoformat()
           } for activity in project.activities.all()]
       }
       
       data['projects'].append(project_data)
   
   response = JsonResponse(data, json_dumps_params={'indent': 2})
   response['Content-Disposition'] = f'attachment; filename="dashboard_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
   return response

@login_required
def get_dashboard_stats(request):
   """Get dashboard statistics via AJAX"""
   projects = Project.objects.filter(team=request.user)
   
   # Calculate detailed statistics
   stats = {
       'total_projects': projects.count(),
       'in_progress': projects.filter(status='in-progress').count(),
       'completed': projects.filter(status='completed').count(),
       'planning': projects.filter(status='planning').count(),
       'on_hold': projects.filter(status='on-hold').count(),
       'overdue_projects': 0,  # Calculate based on end_date vs today
       'avg_progress': 0,
       'total_team_members': 0,
       'active_tasks': 0,
       'completed_tasks': 0
   }
   
   # Calculate additional metrics
   if projects.exists():
       # Overdue projects
       today = datetime.now().date()
       stats['overdue_projects'] = projects.filter(
           end_date__lt=today,
           status__in=['in-progress', 'planning']
       ).count()
       
       # Average progress
       total_progress = 0
       project_count = 0
       for project in projects:
           # Calculate project progress
           total_activities = project.activities.count()
           completed_activities = project.activities.filter(status='completed').count()
           activity_progress = (completed_activities / total_activities * 100) if total_activities > 0 else 0
           
           weeks = project.weeks.all()
           total_weekly_tasks = sum(week.tasks.count() for week in weeks)
           completed_weekly_tasks = sum(week.tasks.filter(status='completed').count() for week in weeks)
           weekly_progress = (completed_weekly_tasks / total_weekly_tasks * 100) if total_weekly_tasks > 0 else 0
           
           project_progress = max(activity_progress, weekly_progress)
           total_progress += project_progress
           project_count += 1
       
       stats['avg_progress'] = int(total_progress / project_count) if project_count > 0 else 0
       
       # Team members count (unique across all projects)
       all_team_members = set()
       for project in projects:
           for member in project.team.all():
               all_team_members.add(member.id)
       stats['total_team_members'] = len(all_team_members)
       
       # Active and completed tasks
       all_weekly_tasks = WeeklyTask.objects.filter(project_week__project__in=projects)
       stats['active_tasks'] = all_weekly_tasks.filter(status__in=['not-started', 'in-progress', 'progressing']).count()
       stats['completed_tasks'] = all_weekly_tasks.filter(status='completed').count()
   
   return JsonResponse(stats)

@login_required
def refresh_dashboard_data(request):
   """Refresh dashboard data via AJAX"""
   # This view can be called periodically to refresh dashboard data
   projects = Project.objects.filter(team=request.user).select_related('created_by').prefetch_related('weeks__tasks', 'activities', 'team')
   recent_activities = Activity.objects.filter(project__in=projects).select_related('project').order_by('-created_at')[:10]
   
   # Serialize projects data
   projects_data = []
   for project in projects:
       weeks_data = []
       for week in project.weeks.all():
           week_tasks = week.tasks.all()
           weeks_data.append({
               'id': week.id,
               'week_number': week.week_number,
               'start_date': week.start_date.isoformat() if week.start_date else None,
               'end_date': week.end_date.isoformat() if week.end_date else None,
               'total_tasks': week_tasks.count(),
               'completed_tasks': week_tasks.filter(status='completed').count(),
               'in_progress_tasks': week_tasks.filter(status__in=['in-progress', 'progressing']).count(),
               'status': 'completed' if week_tasks.count() > 0 and week_tasks.filter(status='completed').count() == week_tasks.count() else 'in-progress' if week_tasks.filter(status__in=['in-progress', 'progressing']).count() > 0 else 'pending'
           })
       
       # Calculate project progress
       total_activities = project.activities.count()
       completed_activities = project.activities.filter(status='completed').count()
       activity_progress = (completed_activities / total_activities * 100) if total_activities > 0 else 0
       
       total_weekly_tasks = sum(week['total_tasks'] for week in weeks_data)
       completed_weekly_tasks = sum(week['completed_tasks'] for week in weeks_data)
       weekly_progress = (completed_weekly_tasks / total_weekly_tasks * 100) if total_weekly_tasks > 0 else 0
       
       calculated_progress = max(activity_progress, weekly_progress)
       
       projects_data.append({
           'id': project.id,
           'name': project.name,
           'client': getattr(project, 'client_name', 'Unknown Client'),
           'status': project.status,
           'progress': int(calculated_progress),
           'start_date': project.start_date.isoformat() if project.start_date else None,
           'end_date': project.end_date.isoformat() if project.end_date else None,
           'weeks': weeks_data
       })
   
   # Serialize activities data
   activities_data = []
   for activity in recent_activities:
       activities_data.append({
           'id': activity.id,
           'title': activity.name,
           'project': activity.project.name,
           'project_id': activity.project.id,
           'status': activity.status,
           'type': getattr(activity, 'activity_type', 'update'),
           'created_at': activity.created_at.isoformat()
       })
   
   return JsonResponse({
       'projects': projects_data,
       'activities': activities_data,
       'stats': {
           'total': projects.count(),
           'in_progress': projects.filter(status='in-progress').count(),
           'completed': projects.filter(status='completed').count(),
           'planning': projects.filter(status='planning').count()
       }
   })


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Project

def update_project_status(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Project.STATUS_CHOICES):
            project.status = new_status
            project.save()
            messages.success(request, 'Project status updated successfully.')
        else:
            messages.error(request, 'Invalid status selected.')
    
    return redirect('main:project_detail', project_id=project.id)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Project

@login_required
def client_page(request):
    # Only show projects where the logged-in user is the assigned client
    projects = Project.objects.filter(client=request.user)

    return render(request, 'client_page.html', {'projects': projects})

@login_required
@require_permission('analytics', 'view')
def analytics(request):
    """Analytics page with project statistics and charts"""
    # Get user's projects
    projects = Project.objects.filter(team=request.user)
    
    # Calculate analytics data
    total_projects = projects.count()
    completed_projects = projects.filter(status='completed').count()
    in_progress_projects = projects.filter(status='in-progress').count()
    planning_projects = projects.filter(status='planning').count()
    on_hold_projects = projects.filter(status='on-hold').count()
    
    # Calculate progress statistics
    total_progress = 0
    project_count = 0
    for project in projects:
        # Calculate project progress
        total_activities = project.activities.count()
        completed_activities = project.activities.filter(status='completed').count()
        activity_progress = (completed_activities / total_activities * 100) if total_activities > 0 else 0
        
        weeks = project.weeks.all()
        total_weekly_tasks = sum(week.tasks.count() for week in weeks)
        completed_weekly_tasks = sum(week.tasks.filter(status='completed').count() for week in weeks)
        weekly_progress = (completed_weekly_tasks / total_weekly_tasks * 100) if total_weekly_tasks > 0 else 0
        
        project_progress = max(activity_progress, weekly_progress)
        total_progress += project_progress
        project_count += 1
    
    avg_progress = int(total_progress / project_count) if project_count > 0 else 0
    
    # Get recent activity data
    recent_activities = Activity.objects.filter(
        project__in=projects
    ).select_related('project').order_by('-created_at')[:10]
    
    # Calculate weekly task statistics
    all_weekly_tasks = WeeklyTask.objects.filter(project_week__project__in=projects)
    total_tasks = all_weekly_tasks.count()
    completed_tasks = all_weekly_tasks.filter(status='completed').count()
    in_progress_tasks = all_weekly_tasks.filter(status__in=['in-progress', 'progressing']).count()
    not_started_tasks = all_weekly_tasks.filter(status='not-started').count()
    
    # Prepare chart data
    status_data = {
        'completed': completed_projects,
        'in_progress': in_progress_projects,
        'planning': planning_projects,
        'on_hold': on_hold_projects
    }
    
    task_status_data = {
        'completed': completed_tasks,
        'in_progress': in_progress_tasks,
        'not_started': not_started_tasks
    }
    
    context = {
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'in_progress_projects': in_progress_projects,
        'planning_projects': planning_projects,
        'on_hold_projects': on_hold_projects,
        'avg_progress': avg_progress,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'not_started_tasks': not_started_tasks,
        'recent_activities': recent_activities,
        'status_data': status_data,
        'task_status_data': task_status_data,
    }
    
    return render(request, 'analytics.html', context)

@login_required
@require_permission('team', 'view')
def team(request):
    """Teams page to view all team members"""
    # Get all users (team members)
    team_members = User.objects.all().order_by('username')
    
    # Get projects for each team member
    for member in team_members:
        member.project_count = member.projects.count()
        member.active_projects = member.projects.filter(status='in-progress').count()
    
    context = {
        'team_members': team_members,
    }
    return render(request, 'team.html', context)

@login_required
def admin_control(request):
    """Admin control center for managing user access"""
    # Check if user is admin (you can customize this logic)
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('main:dashboard')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
        try:
            user = User.objects.get(id=user_id)
            previous_values = {
                'is_active': user.is_active,
                'can_login': user.can_login,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff
            }
            
            if action == 'enable':
                user.is_active = True
                user.can_login = True
                SystemLog.log_action(
                    user=request.user,
                    action='user_updated',
                    target_model='User',
                    target_id=user.id,
                    target_name=f"{user.username} (Enabled)",
                    previous_values=previous_values,
                    new_values={'is_active': True, 'can_login': True},
                    request=request
                )
                messages.success(request, f'{user.username} access enabled.')
            elif action == 'disable':
                user.is_active = False
                user.can_login = False
                SystemLog.log_action(
                    user=request.user,
                    action='user_updated',
                    target_model='User',
                    target_id=user.id,
                    target_name=f"{user.username} (Disabled)",
                    previous_values=previous_values,
                    new_values={'is_active': False, 'can_login': False},
                    request=request
                )
                messages.success(request, f'{user.username} access disabled.')
            elif action == 'grant_access':
                user.can_login = True
                SystemLog.log_action(
                    user=request.user,
                    action='access_granted',
                    target_model='User',
                    target_id=user.id,
                    target_name=f"{user.username} (Access Granted)",
                    previous_values=previous_values,
                    new_values={'can_login': True},
                    request=request
                )
                messages.success(request, f'{user.username} login access granted.')
            elif action == 'deny_access':
                user.can_login = False
                SystemLog.log_action(
                    user=request.user,
                    action='access_denied',
                    target_model='User',
                    target_id=user.id,
                    target_name=f"{user.username} (Access Denied)",
                    previous_values=previous_values,
                    new_values={'can_login': False},
                    request=request
                )
                messages.success(request, f'{user.username} login access denied.')
            elif action == 'make_admin':
                user.is_superuser = True
                user.is_staff = True
                user.can_login = True
                SystemLog.log_action(
                    user=request.user,
                    action='admin_made',
                    target_model='User',
                    target_id=user.id,
                    target_name=f"{user.username} (Made Admin)",
                    previous_values=previous_values,
                    new_values={'is_superuser': True, 'is_staff': True, 'can_login': True},
                    request=request
                )
                messages.success(request, f'{user.username} is now an admin.')
            elif action == 'remove_admin':
                user.is_superuser = False
                user.is_staff = False
                SystemLog.log_action(
                    user=request.user,
                    action='admin_removed',
                    target_model='User',
                    target_id=user.id,
                    target_name=f"{user.username} (Admin Removed)",
                    previous_values=previous_values,
                    new_values={'is_superuser': False, 'is_staff': False},
                    request=request
                )
                messages.success(request, f'{user.username} admin privileges removed.')
            
            user.save()
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
    
    # Get all users for admin management
    users = User.objects.all().order_by('username')
    
    context = {
        'users': users,
    }
    return render(request, 'admin_control.html', context)

@login_required
@require_permission('system_logs', 'view')
def system_logs(request):
    """View system logs with filtering and search"""
    # Check if user is admin
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('main:dashboard')
    
    # Get filter parameters
    action_filter = request.GET.get('action', '')
    user_filter = request.GET.get('user', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search = request.GET.get('search', '')
    
    # Base queryset
    logs = SystemLog.objects.select_related('user').all()
    
    # Apply filters
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            logs = logs.filter(created_at__date__gte=from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            logs = logs.filter(created_at__date__lte=to_date)
        except ValueError:
            pass
    
    if search:
        logs = logs.filter(
            models.Q(target_name__icontains=search) |
            models.Q(user__username__icontains=search) |
            models.Q(action__icontains=search)
        )
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(logs, 50)  # 50 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get available actions for filter
    available_actions = SystemLog.ACTION_CHOICES
    
    context = {
        'page_obj': page_obj,
        'action_filter': action_filter,
        'user_filter': user_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search': search,
        'available_actions': available_actions,
        'total_logs': logs.count(),
    }
    
    return render(request, 'system_logs.html', context)

# Working DonutChart implementation with red/black/white theme - centered and bigger
def create_donut_chart(progress_percentage):
    """Create a centered, bigger donut chart with red/black/white theme for one-page layout"""
    try:
        drawing = Drawing(400, 150)  # Bigger size and centered
        pie = Pie()
        pie.x = 130  # Centered horizontally
        pie.y = 15
        pie.width = 120  # Bigger chart
        pie.height = 120
        
        # Ensure valid progress data
        progress = max(0, min(100, float(progress_percentage or 0)))
        remaining = 100 - progress
        
        # Create donut chart showing completed vs remaining
        pie.data = [progress, remaining] if remaining > 0 else [progress]
        pie.labels = ['', '']
        pie.slices[0].fillColor = colors.HexColor('#dc2626')  # Red for progress
        if remaining > 0:
            pie.slices[1].fillColor = colors.HexColor('#000000')  # Black for remaining
        
        pie.slices.strokeColor = colors.white
        pie.slices.strokeWidth = 2
        drawing.add(pie)
        
        # Add center circle for donut effect
        cx, cy = 190, 75  # Centered
        ring = Circle(cx, cy, 40, fillColor=colors.white, strokeColor=colors.white)  # Bigger center
        drawing.add(ring)
        
        # Add percentage in center
        pct_label = String(cx, cy - 4, f"{progress:.1f}%", textAnchor='middle')
        pct_label.fontName = 'Helvetica-Bold'
        pct_label.fontSize = 16  # Bigger text
        pct_label.fillColor = colors.HexColor('#000000')  # Black text
        drawing.add(pct_label)
        
        return drawing
    except Exception:
        # Return empty drawing if chart creation fails
        return Drawing(400, 150)

def generate_project_pdf(project):
    """Generate an email-style PDF report that matches the exact format shown in the image"""
    # Create filename with date
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f"ProjectReport_{project.name.replace(' ', '_')}_{today}.pdf"
    
    # Create PDF document
    doc = SimpleDocTemplate(
        filename, 
        pagesize=A4,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Email-style title (RED like in image)
    title_style = ParagraphStyle(
        'EmailTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=8,
        spaceBefore=0,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#dc2626'),  # Red color like in image
        fontName='Helvetica-Bold'
    )
    
    # Subtitle style (gray)
    subtitle_style = ParagraphStyle(
        'EmailSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#6b7280'),
        fontName='Helvetica'
    )
    
    # Red/Black/White Email greeting style
    greeting_style = ParagraphStyle(
        'EmailGreeting',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        textColor=colors.HexColor('#000000'),  # Black text
        fontName='Helvetica-Bold'
    )
    
    # Red/Black/White Email body style
    body_style = ParagraphStyle(
        'EmailBody',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=6,
        textColor=colors.HexColor('#000000'),  # Black text
        fontName='Helvetica',
        leading=12
    )
    
    # Red/Black/White Section heading style
    section_heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=11,
        spaceAfter=4,
        spaceBefore=8,
        textColor=colors.HexColor('#dc2626'),  # Red headings
        fontName='Helvetica-Bold'
    )
    
    # Calculate project metrics
    total_activities = project.activities.count()
    completed_activities = project.activities.filter(status='completed').count()
    activity_progress = (completed_activities / total_activities * 100) if total_activities > 0 else 0
    
    weeks = project.weeks.all()
    total_weekly_tasks = sum(week.tasks.count() for week in weeks)
    completed_weekly_tasks = sum(week.tasks.filter(status='completed').count() for week in weeks)
    weekly_progress = (completed_weekly_tasks / total_weekly_tasks * 100) if total_weekly_tasks > 0 else 0
    
    overall_progress = max(activity_progress, weekly_progress)
    
    # Calculate totals for summary table
    total_projects = 1
    completed_projects = 1 if project.status == 'completed' else 0
    projects_in_progress = 1 if project.status == 'in-progress' else 0
    
    # EMAIL HEADER (project-specific)
    story.append(Paragraph(f"Project Report: {project.name}", title_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
    
    # EMAIL GREETING
    # Try to get client name from project's created_by user or default
    if hasattr(project, 'created_by') and project.created_by:
        client_name = project.created_by.username or project.created_by.first_name or 'Client'
    else:
        client_name = 'Client'
    story.append(Paragraph(f"Dear {client_name},", greeting_style))
    story.append(Spacer(1, 10))
    
    # DONUT CHART (centered, showing project progress)
    donut_chart = create_donut_chart(overall_progress)
    story.append(donut_chart)
    story.append(Spacer(1, 20))
    
    # EMAIL BODY TEXT (project-specific)
    story.append(Paragraph(f"Please find the progress summary for your project '{project.name}' below.", body_style))
    story.append(Spacer(1, 16))
    
    # PROJECT-SPECIFIC SUMMARY TABLE
    project_status = getattr(project, 'get_status_display', lambda: getattr(project, 'status', 'Unknown'))()
    
    summary_data = [
        ['Project Details', 'Information'],
        ['Project Name', project.name or 'N/A'],
        ['Current Status', project_status],
        ['Total Activities', str(total_activities)],
        ['Completed Activities', str(completed_activities)],
        ['Total Weekly Tasks', str(total_weekly_tasks)],
        ['Completed Weekly Tasks', str(completed_weekly_tasks)],
        ['Overall Progress', f'{overall_progress:.1f}%']
    ]
    
    summary_table = Table(summary_data, colWidths=[4.5*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        # Header row (dark)
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        
        # Data rows (alternating)
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        
        # Grid lines
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # PROJECT HIGHLIGHTS SECTION
    story.append(Paragraph("Project Highlights", section_heading_style))
    highlights_text = f"""• Your project '{project.name}' shows {overall_progress:.1f}% overall completion progress.<br/>
• Current project status: {project_status}.<br/>
• Activities completed: {completed_activities} out of {total_activities} total activities.<br/>
• Weekly tasks completed: {completed_weekly_tasks} out of {total_weekly_tasks} total tasks."""
    story.append(Paragraph(highlights_text, body_style))
    story.append(Spacer(1, 16))
    
    # PROJECT NEXT STEPS SECTION
    story.append(Paragraph("Next Steps", section_heading_style))
    next_steps_text = f"""• Continue monitoring progress on '{project.name}' to maintain momentum.<br/>
• Reply with any specific priorities you'd like us to focus on for this project.<br/>
• Schedule a project review if you'd like to discuss any adjustments or requirements."""
    story.append(Paragraph(next_steps_text, body_style))
    story.append(Spacer(1, 16))
    
    # EMAIL CLOSING
    closing_text = """If you have any questions, simply reply to this email and our team will assist you.<br/><br/>
Warm regards,<br/><br/>
E-Click Project Management Team"""
    story.append(Paragraph(closing_text, body_style))
    story.append(Spacer(1, 20))
    
    # FOOTER BANNER (exactly like image)
    footer_banner = Table([["WE CARE, WE CAN, WE DELIVER"]], colWidths=[6*inch])
    footer_banner.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(footer_banner)
    
    # Build PDF
    doc.build(story)
    return filename

@login_required
def generate_project_report(request, project_id):
    """Generate and download PDF report for a project"""
    project = get_object_or_404(Project, id=project_id, team=request.user)
    
    # Generate PDF
    filename = generate_project_pdf(project)
    
    # Read the generated file
    with open(filename, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Clean up the temporary file
    os.remove(filename)
    
    # Log the report generation
    SystemLog.log_action(
        user=request.user,
        action='data_export',
        target_model='Project',
        target_id=project.id,
        target_name=f"PDF Report - {project.name}",
        request=request
    )
    
    return response

@login_required
def send_project_report_email(request, project_id):
    """Send project report via email"""
    project = get_object_or_404(Project, id=project_id, team=request.user)
    
    if request.method == 'POST':
        recipient_email = request.POST.get('recipient_email')
        
        if not recipient_email:
            messages.error(request, 'Recipient email is required')
            return redirect('main:project_detail', project_id=project.id)
        
        try:
            # Generate PDF
            filename = generate_project_pdf(project)
            
            # Read the PDF file
            with open(filename, 'rb') as f:
                pdf_content = f.read()
            
            # Send email
            subject = f'Project Progress Report - {project.name}'
            message = f"""
            Dear Client,
            
            Please find attached the progress report for project "{project.name}".
            
            Project Details:
            - Client: {project.client}
            - Status: {project.status.title()}
            - Progress: {project.progress}%
            
            If you have any questions, please don't hesitate to contact us.
            
            Best regards,
            The Project Management Team
            """
            
            # Send email with PDF attachment
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            
            # Clean up the temporary file
            os.remove(filename)
            
            # Log the email sending
            SystemLog.log_action(
                user=request.user,
                action='data_export',
                target_model='Project',
                target_id=project.id,
                target_name=f"Email Report - {project.name} to {recipient_email}",
                request=request
            )
            
            messages.success(request, f'Report sent successfully to {recipient_email}')
            
        except Exception as e:
            messages.error(request, f'Failed to send email: {str(e)}')
            # Clean up file if it exists
            if os.path.exists(filename):
                os.remove(filename)
    
    return redirect('main:project_detail', project_id=project.id)

@login_required
def contact_project_owner(request, project_id):
    """Contact the project owner via email"""
    project = get_object_or_404(Project, id=project_id, team=request.user)
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if not subject or not message:
            messages.error(request, 'Subject and message are required')
            return redirect('main:project_detail', project_id=project.id)
        
        try:
            # Send email to project owner
            email_message = f"""
            Message from {request.user.username} ({request.user.email}) regarding project "{project.name}":
            
            Subject: {subject}
            
            Message:
            {message}
            
            Project Details:
            - Project: {project.name}
            - Client: {project.client}
            - Status: {project.status}
            - Progress: {project.progress}%
            """
            
            send_mail(
                subject=f'Project Inquiry: {subject}',
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[project.created_by.email],
                fail_silently=False,
            )
            
            # Log the contact
            SystemLog.log_action(
                user=request.user,
                action='user_updated',
                target_model='Project',
                target_id=project.id,
                target_name=f"Contact Owner - {project.name}",
                request=request
            )
            
            messages.success(request, 'Message sent successfully to project owner')
            
        except Exception as e:
            messages.error(request, f'Failed to send message: {str(e)}')
    
    return redirect('main:project_detail', project_id=project.id)

@login_required
def send_client_email_ajax(request):
    """Send client email via AJAX"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        client_email = data.get('client_email')
        project_name = data.get('project_name')
        
        try:
            # Find the project
            project = Project.objects.filter(client_email=client_email, name=project_name).first()
            if not project:
                return JsonResponse({'success': False, 'message': 'Project not found'})
            
            # Generate and send PDF report
            filename = generate_project_pdf(project)
            
            # Send email
            subject = f'Project Progress Report - {project.name}'
            message = f"""
            Dear Client,
            
            Please find attached the progress report for project "{project.name}".
            
            Project Details:
            - Client: {project.client}
            - Status: {project.status.title()}
            - Progress: {project.progress}%
            
            If you have any questions, please don't hesitate to contact us.
            
            Best regards,
            The Project Management Team
            """
            
            # Send email with PDF attachment
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client_email],
                fail_silently=False,
            )
            
            # Clean up the temporary file
            os.remove(filename)
            
            # Log the email sending
            SystemLog.log_action(
                user=request.user,
                action='data_export',
                target_model='Project',
                target_id=project.id,
                target_name=f"Email Report - {project.name} to {client_email}",
                request=request
            )
            
            return JsonResponse({'success': True, 'message': 'Email sent successfully'})
            
        except Exception as e:
            # Clean up file if it exists
            if 'filename' in locals() and os.path.exists(filename):
                os.remove(filename)
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def permission_management(request):
    """Manage user permissions"""
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can manage permissions.')
        return redirect('main:dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        section = request.POST.get('section')
        permission = request.POST.get('permission')
        
        try:
            user = User.objects.get(id=user_id)
            
            if action == 'grant':
                UserPermission.grant_permission(user, section, permission, request.user)
                SystemLog.log_action(
                    user=request.user,
                    action='permission_granted',
                    target_model='UserPermission',
                    target_id=user.id,
                    target_name=f"{permission} permission for {section} granted to {user.username}",
                    new_values={'section': section, 'permission': permission},
                    request=request
                )
                messages.success(request, f'Permission granted to {user.username}')
            
            elif action == 'revoke':
                UserPermission.revoke_permission(user, section, permission)
                SystemLog.log_action(
                    user=request.user,
                    action='permission_revoked',
                    target_model='UserPermission',
                    target_id=user.id,
                    target_name=f"{permission} permission for {section} revoked from {user.username}",
                    new_values={'section': section, 'permission': permission},
                    request=request
                )
                messages.success(request, f'Permission revoked from {user.username}')
                
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    # Get all users and their permissions
    users = User.objects.filter(is_active=True).order_by('username')
    sections = UserPermission.SECTION_CHOICES
    permissions = UserPermission.PERMISSION_CHOICES
    
    # Get current permissions for each user
    user_permissions = {}
    for user in users:
        user_permissions[user.id] = UserPermission.objects.filter(user=user, is_active=True)
    
    context = {
        'users': users,
        'sections': sections,
        'permissions': permissions,
        'user_permissions': user_permissions,
    }
    
    return render(request, 'permission_management.html', context)

@login_required
def user_permissions(request, user_id):
    """View specific user's permissions"""
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can view user permissions.')
        return redirect('main:dashboard')
    
    user = get_object_or_404(User, id=user_id)
    permissions = UserPermission.objects.filter(user=user).order_by('section', 'permission')
    
    context = {
        'target_user': user,
        'permissions': permissions,
        'sections': UserPermission.SECTION_CHOICES,
        'permission_types': UserPermission.PERMISSION_CHOICES,
    }
    
    return render(request, 'user_permissions.html', context)
