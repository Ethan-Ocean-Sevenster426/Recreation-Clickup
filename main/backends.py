# main/backends.py
from django.contrib.auth.backends import ModelBackend
from .models import User

class EmailBackend(ModelBackend):
    """Custom authentication backend to login with email or username"""
    
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        if not username or not password:
            return None
            
        try:
            # First, try to find user by email
            if '@' in username:
                user = User.objects.get(email=username)
            else:
                # Try to find user by username
                user = User.objects.get(username=username)
            
            # Check password and user status
            if user.check_password(password) and user.is_active and user.can_login:
                return user
                
        except User.DoesNotExist:
            # If user not found by username, try by email
            try:
                user = User.objects.get(email=username)
                if user.check_password(password) and user.is_active and user.can_login:
                    return user
            except User.DoesNotExist:
                pass
                
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id, is_active=True)
        except User.DoesNotExist:
            return None