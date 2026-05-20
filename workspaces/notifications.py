"""
Email notifications via Microsoft Graph API (Azure AD client-credentials flow).

Sends HTML emails when:
  - A task field is updated  → notifies all assignees (excluding the person who made the change)
  - A comment is added       → notifies all assignees + previous commenters (excluding author)
"""

import logging
import random
import string
import threading

import msal
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

_token_cache = msal.SerializableTokenCache()


def _get_access_token():
    """Acquire a Graph API access token using client credentials."""
    tenant = getattr(settings, 'AZURE_TENANT_ID', '')
    client_id = getattr(settings, 'AZURE_CLIENT_ID', '')
    secret = getattr(settings, 'AZURE_CLIENT_SECRET', '')
    if not all([tenant, client_id, secret]):
        return None

    authority = f'https://login.microsoftonline.com/{tenant}'
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=secret,
        token_cache=_token_cache,
    )
    # Try cache first
    result = app.acquire_token_silent(['https://graph.microsoft.com/.default'], account=None)
    if not result:
        result = app.acquire_token_for_client(scopes=['https://graph.microsoft.com/.default'])

    if 'access_token' in result:
        return result['access_token']

    logger.error('Failed to acquire Graph token: %s', result.get('error_description', result))
    return None


def _send_graph_email(to_emails, subject, html_body):
    """Send an email via Microsoft Graph /sendMail endpoint."""
    sender = getattr(settings, 'AZURE_MAIL_FROM', '')
    if not sender or not to_emails:
        return

    token = _get_access_token()
    if not token:
        logger.warning('No Graph token – skipping email to %s', to_emails)
        return

    recipients = [{'emailAddress': {'address': e}} for e in to_emails if e]
    payload = {
        'message': {
            'subject': subject,
            'body': {'contentType': 'HTML', 'content': html_body},
            'toRecipients': recipients,
        },
        'saveToSentItems': 'false',
    }

    url = f'https://graph.microsoft.com/v1.0/users/{sender}/sendMail'
    resp = requests.post(
        url,
        json=payload,
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        timeout=15,
    )
    if resp.status_code == 202:
        logger.info('Email sent to %s — %s', to_emails, subject)
    else:
        logger.error('Graph sendMail failed (%s): %s', resp.status_code, resp.text)


def _send_async(to_emails, subject, html_body):
    """Fire-and-forget email in a background thread so the view isn't blocked."""
    t = threading.Thread(target=_send_graph_email, args=(to_emails, subject, html_body), daemon=True)
    t.start()


# ── Public helpers called from views ──────────────────────────────────────────

def _task_url(task):
    """Build an absolute URL to a task (best-effort; assumes localhost in dev)."""
    base = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
    return f'{base}/workspaces/tasks/{task.id}/'


def _email_html(title, lines, task):
    """Wrap notification content in a simple styled HTML email."""
    url = _task_url(task)
    body_lines = ''.join(f'<p style="margin:4px 0;color:#333;">{l}</p>' for l in lines)
    return f'''
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:560px;margin:0 auto;">
        <div style="background:#6347EA;padding:16px 24px;border-radius:8px 8px 0 0;">
            <span style="color:#fff;font-size:18px;font-weight:600;">Luma</span>
        </div>
        <div style="background:#ffffff;padding:24px;border:1px solid #e5e5e5;border-top:none;border-radius:0 0 8px 8px;">
            <h2 style="margin:0 0 12px;font-size:16px;color:#1A1639;">{title}</h2>
            {body_lines}
            <a href="{url}" style="display:inline-block;margin-top:16px;padding:10px 20px;background:#6347EA;color:#fff;text-decoration:none;border-radius:6px;font-size:14px;font-weight:500;">
                View Task
            </a>
        </div>
        <p style="text-align:center;margin-top:12px;font-size:11px;color:#999;">
            You received this because you are involved in this task.
        </p>
    </div>
    '''


def _create_in_app(recipient_users, actor, verb, description, task):
    """Create in-app Notification records for each recipient."""
    from .models import Notification
    if not recipient_users:
        print('[NOTIFY] No recipients — skipping in-app notification')
        return
    usernames = [u.username for u in recipient_users]
    print(f'[NOTIFY] Creating in-app notifications for {usernames} — "{description}"')
    Notification.objects.bulk_create([
        Notification(recipient=u, actor=actor, verb=verb, description=description, task=task)
        for u in recipient_users
    ])
    print('[NOTIFY] In-app notifications created OK')


def notify_task_updated(task, changed_by, field, old_value, new_value):
    """Notify all task assignees (including the changer) when a field changes."""
    assignees = list(task.assignees.all())
    print(f'[NOTIFY] notify_task_updated called — task={task.title} field={field} assignees={[u.username for u in assignees]} changed_by={changed_by.username}')

    if not assignees:
        print('[NOTIFY] No assignees — skipping notification')
        return

    field_display = field.replace('_', ' ').title()

    # In-app notifications
    desc = f'changed {field_display} from "{old_value or "—"}" to "{new_value or "—"}" on {task.title}'
    _create_in_app(assignees, changed_by, 'update', desc, task)

    # Email notifications
    recipients = [u.email for u in assignees if u.email]
    if not recipients:
        print('[NOTIFY] No email recipients — skipping email')
        return

    title = f'Task Updated: {task.title}'
    lines = [
        f'<strong>{changed_by.get_full_name() or changed_by.username}</strong> updated <strong>{field_display}</strong>.',
        f'<span style="color:#999;">{old_value or "—"}</span> → <strong>{new_value or "—"}</strong>',
        f'<span style="color:#888;">List: {task.task_list.name}</span>',
    ]
    html = _email_html(title, lines, task)
    _send_async(recipients, f'[Luma] {title}', html)


def notify_assigned(task, assigned_by, new_assignees):
    """Notify only newly-added assignees that they have been assigned to a task."""
    # Exclude the person who did the assigning (they already know)
    recipients = [u for u in new_assignees if u != assigned_by]
    if not recipients:
        return

    # In-app notifications
    desc = f'assigned you to "{task.title}"'
    _create_in_app(recipients, assigned_by, 'update', desc, task)

    # Email notifications
    email_recipients = [u.email for u in recipients if u.email]
    if not email_recipients:
        return

    title = f'You\'ve been assigned: {task.title}'
    lines = [
        f'<strong>{assigned_by.get_full_name() or assigned_by.username}</strong> assigned you to this task.',
        f'<span style="color:#888;">List: {task.task_list.name}</span>',
    ]
    html = _email_html(title, lines, task)
    _send_async(email_recipients, f'[Luma] {title}', html)


def notify_task_completed(task, completed_by):
    """Notify all task assignees (including the completer) that the task is done."""
    assignees = list(task.assignees.all())
    print(f'[NOTIFY] notify_task_completed called — task={task.title} assignees={[u.username for u in assignees]} completed_by={completed_by.username}')

    if not assignees:
        print('[NOTIFY] No assignees — skipping completion notification')
        return

    # In-app notifications
    desc = f'marked "{task.title}" as done'
    _create_in_app(assignees, completed_by, 'update', desc, task)

    # Email notifications
    recipients = [u.email for u in assignees if u.email]
    if not recipients:
        print('[NOTIFY] No email recipients — skipping email')
        return

    title = f'Task Completed: {task.title}'
    lines = [
        f'<strong>{completed_by.get_full_name() or completed_by.username}</strong> marked this task as <strong style="color:#16a34a;">Done</strong>.',
        f'<span style="color:#888;">List: {task.task_list.name}</span>',
    ]
    html = _email_html(title, lines, task)
    _send_async(recipients, f'[Luma] {title}', html)


def _otp_email_html(user, otp_code, is_new_user=True):
    """Build styled HTML email for OTP delivery."""
    base = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
    verify_url = f'{base}/workspaces/otp/verify/'
    display_name = user.get_full_name() or user.email
    if is_new_user:
        heading = 'Welcome to Luma!'
        intro = f'An account has been created for you, <strong>{display_name}</strong>.'
        action_text = 'Set up your account'
    else:
        heading = 'Password Reset'
        intro = f'A password reset was requested for <strong>{display_name}</strong>.'
        action_text = 'Reset your password'

    return f'''
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:560px;margin:0 auto;">
        <div style="background:#6347EA;padding:16px 24px;border-radius:8px 8px 0 0;">
            <span style="color:#fff;font-size:18px;font-weight:600;">Luma</span>
        </div>
        <div style="background:#ffffff;padding:24px;border:1px solid #e5e5e5;border-top:none;border-radius:0 0 8px 8px;">
            <h2 style="margin:0 0 12px;font-size:16px;color:#1A1639;">{heading}</h2>
            <p style="margin:4px 0;color:#333;">{intro}</p>
            <p style="margin:4px 0;color:#333;">{action_text} using this one-time code:</p>
            <div style="text-align:center;margin:20px 0;">
                <span style="display:inline-block;font-size:32px;font-weight:700;letter-spacing:8px;color:#6347EA;background:#F5F4FA;padding:14px 28px;border-radius:8px;border:2px dashed #6347EA;">{otp_code}</span>
            </div>
            <p style="margin:4px 0;color:#888;font-size:13px;">This code expires in 24 hours.</p>
            <a href="{verify_url}" style="display:inline-block;margin-top:16px;padding:10px 20px;background:#6347EA;color:#fff;text-decoration:none;border-radius:6px;font-size:14px;font-weight:500;">
                {action_text}
            </a>
        </div>
        <p style="text-align:center;margin-top:12px;font-size:11px;color:#999;">
            If you did not request this, you can safely ignore this email.
        </p>
    </div>
    '''


def generate_otp():
    """Generate a 6-digit numeric OTP."""
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(user, otp_code, is_new_user=True):
    """Send OTP code to a user via email (async)."""
    if not user.email:
        print(f'[OTP] No email for {user.username} — skipping')
        return

    subject = '[Luma] Set up your account' if is_new_user else '[Luma] Password reset code'
    html = _otp_email_html(user, otp_code, is_new_user)

    # Try Graph API first, fall back to Django send_mail
    sender = getattr(settings, 'AZURE_MAIL_FROM', '')
    if sender and getattr(settings, 'AZURE_TENANT_ID', ''):
        _send_async([user.email], subject, html)
    else:
        # Use Django's email backend (console in dev)
        from django.core.mail import send_mail as django_send_mail
        try:
            django_send_mail(
                subject,
                f'Your Luma OTP code is: {otp_code}',
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@luma.dev'),
                [user.email],
                html_message=html,
                fail_silently=True,
            )
            print(f'[OTP] Email sent to {user.email} via Django backend')
        except Exception as e:
            print(f'[OTP] Email failed: {e}')


def notify_comment_added(task, comment):
    """Notify all assignees + previous commenters when a new comment is posted."""
    author = comment.author
    recipient_users = set()

    # All assignees
    for assignee in task.assignees.all():
        if assignee != author:
            recipient_users.add(assignee)

    # Previous commenters (excluding the author of this comment)
    for c in task.comments.select_related('author').exclude(author=author):
        if c.author != author:
            recipient_users.add(c.author)

    # In-app notifications
    desc = f'commented on {task.title}: "{comment.body[:80]}"'
    _create_in_app(list(recipient_users), author, 'comment', desc, task)

    # Email notifications
    email_recipients = [u.email for u in recipient_users if u.email]
    if not email_recipients:
        return

    title = f'New Comment on: {task.title}'
    lines = [
        f'<strong>{author.get_full_name() or author.username}</strong> commented:',
        f'<div style="background:#F5F4FA;padding:10px 14px;border-radius:6px;margin:8px 0;white-space:pre-wrap;">{comment.body}</div>',
        f'<span style="color:#888;">List: {task.task_list.name}</span>',
    ]
    html = _email_html(title, lines, task)
    _send_async(email_recipients, f'[Luma] {title}', html)
