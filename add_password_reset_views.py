#!/usr/bin/env python
"""Add password reset views to views.py"""

password_reset_code = '''

# Password Reset Views
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail

def password_reset_request(request):
    """Handle password reset request"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'home/password_reset.html')

        # Try to find user by email (both User and Client)
        user = None
        is_client = False

        # Check Django users first
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Check clients
            try:
                user = Client.objects.get(email=email)
                is_client = True
            except Client.DoesNotExist:
                pass

        if user:
            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Build reset URL
            reset_url = request.build_absolute_uri(
                f'/password-reset-confirm/{uid}/{token}/'
            )

            # Send email
            subject = 'Password Reset Request - E-Click'
            message = f"""Hello,

You have requested to reset your password for E-Click.

Click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you did not request this password reset, please ignore this email.

Best regards,
E-Click Team"""

            try:
                send_mail(
                    subject,
                    message,
                    django_settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'Password reset email sent! Please check your inbox.')
                return redirect('password_reset_done')
            except Exception as e:
                messages.error(request, f'Error sending email: {str(e)}')
                return render(request, 'home/password_reset.html')
        else:
            # Don't reveal if email exists or not (security best practice)
            messages.success(request, 'If an account with that email exists, a password reset link has been sent.')
            return redirect('password_reset_done')

    return render(request, 'home/password_reset.html')

def password_reset_done(request):
    """Show confirmation that reset email was sent"""
    return render(request, 'home/password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    """Handle password reset with token"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))

        # Try User first
        user = None
        is_client = False
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            try:
                user = Client.objects.get(pk=uid)
                is_client = True
            except Client.DoesNotExist:
                user = None

        if user and default_token_generator.check_token(user, token):
            if request.method == 'POST':
                password1 = request.POST.get('password1')
                password2 = request.POST.get('password2')

                if password1 != password2:
                    messages.error(request, 'Passwords do not match.')
                    return render(request, 'home/password_reset_confirm.html')

                if len(password1) < 8:
                    messages.error(request, 'Password must be at least 8 characters long.')
                    return render(request, 'home/password_reset_confirm.html')

                # Set new password
                if is_client:
                    from django.contrib.auth.hashers import make_password
                    user.password = make_password(password1)
                    user.save()
                else:
                    user.set_password(password1)
                    user.save()

                messages.success(request, 'Password reset successful! You can now login with your new password.')
                return redirect('password_reset_complete')

            return render(request, 'home/password_reset_confirm.html')
        else:
            messages.error(request, 'Invalid or expired password reset link.')
            return redirect('password_reset')

    except Exception as e:
        messages.error(request, 'Invalid password reset link.')
        return redirect('password_reset')

def password_reset_complete(request):
    """Show confirmation that password was reset"""
    return render(request, 'home/password_reset_complete.html')
'''

# Read the current views.py
with open(r'c:\Users\Ethan\Downloads\Django-E-Click-master (5)\Django-E-Click-master\home\views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Append the password reset views
with open(r'c:\Users\Ethan\Downloads\Django-E-Click-master (5)\Django-E-Click-master\home\views.py', 'a', encoding='utf-8') as f:
    f.write(password_reset_code)

print("Password reset views added to views.py!")
