import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def fix_user_password():
    try:
        # Get User 2
        user = User.objects.get(username='User 2')
        
        # Set password
        user.set_password('testpass123')
        user.save()
        
        print("✅ Password set successfully!")
        print(f"Username: {user.username}")
        print(f"Password: testpass123")
        print(f"Email: {user.email}")
        print(f"Active: {user.is_active}")
        print(f"Staff: {user.is_staff}")
        
        # Check projects
        from home.models import Project
        projects = user.assigned_projects.all()
        if projects:
            print(f"Assigned Projects: {[p.name for p in projects]}")
        else:
            print("No projects assigned")
            
        return True
        
    except User.DoesNotExist:
        print("❌ User 'User 2' not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Setting password for User 2...")
    success = fix_user_password()
    if success:
        print("\n🎉 You can now login with:")
        print("Username: User 2")
        print("Password: testpass123")
        print("\n🌐 Open your browser and go to: http://localhost:8000/login/")
    else:
        print("\n❌ Failed to set password")
