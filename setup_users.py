import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def setup_users():
    users_to_setup = [
        {'username': 'ethan', 'password': 'ethan123'},
        {'username': 'User 2', 'password': 'user2123'}
    ]
    
    for user_info in users_to_setup:
        try:
            user = User.objects.get(username=user_info['username'])
            user.set_password(user_info['password'])
            user.save()
            
            print(f"✅ Password set for {user.username}: {user_info['password']}")
            print(f"   Email: {user.email}")
            print(f"   Active: {user.is_active}")
            print(f"   Staff: {user.is_staff}")
            
            # Check assigned projects
            from home.models import Project
            projects = user.assigned_projects.all()
            if projects:
                print(f"   Assigned Projects: {[p.name for p in projects]}")
            else:
                print("   No projects assigned")
            print()
            
        except User.DoesNotExist:
            print(f"❌ User '{user_info['username']}' not found")
        except Exception as e:
            print(f"❌ Error setting password for {user_info['username']}: {e}")

if __name__ == "__main__":
    print("Setting up user passwords...")
    print("=" * 40)
    setup_users()
    print("=" * 40)
    print("🎉 You can now login with:")
    print("Username: ethan, Password: ethan123")
    print("Username: User 2, Password: user2123")
    print("\n🌐 Open your browser and go to: http://localhost:8000/login/")
