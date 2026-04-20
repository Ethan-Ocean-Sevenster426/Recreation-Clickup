#!/usr/bin/env python3
"""
Script to identify the Google account associated with OAuth2 credentials
"""

import os
import sys
import django
from pathlib import Path

# Add Django project to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

def get_oauth2_account_info():
    """Get information about the OAuth2 account"""
    try:
        print("🔍 Identifying OAuth2 account...")
        
        # Path to credentials file
        credentials_path = os.path.join('home', 'credentials.json')
        
        if not os.path.exists(credentials_path):
            print(f"❌ Credentials file not found at: {credentials_path}")
            print("📝 Please ensure your credentials.json file is in the home/ directory")
            return
        
        print(f"✅ Found credentials file at: {credentials_path}")
        
        # Gmail API scopes - Google automatically adds 'openid' scope
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.readonly',  # Needed for profile access
            'https://www.googleapis.com/auth/userinfo.email',
            'openid'  # Google automatically adds this
        ]
        
        # Check if we have a token file
        token_path = os.path.join('home', 'token.pickle')
        creds = None
        
        if os.path.exists(token_path):
            print("✅ Found existing token file")
            try:
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                print(f"⚠️  Error loading token: {e}")
                creds = None
        
        # If no valid credentials, start OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Refreshing expired token...")
                try:
                    creds.refresh(Request())
                    print("✅ Token refreshed successfully")
                except Exception as e:
                    print(f"❌ Error refreshing token: {e}")
                    creds = None
            
            if not creds:
                print("🔐 Starting OAuth flow...")
                print("🌐 This will open a browser window for authentication")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                
                # Use the exact redirect URI that matches Google Cloud Console
                creds = flow.run_local_server(port=55691, prompt='consent', redirect_uri_trailing_slash=False)
                print("✅ OAuth flow completed successfully!")
            
            # Save credentials
            try:
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
                print("💾 Token saved for future use")
            except Exception as e:
                print(f"⚠️  Warning: Could not save token: {e}")
        
        # Build Gmail service
        service = build('gmail', 'v1', credentials=creds)
        
        # Get user profile
        print("📧 Getting account information...")
        user_info = service.users().getProfile(userId='me').execute()
        
        print("\n🎉 OAuth2 Account Information:")
        print(f"   📧 Email: {user_info.get('emailAddress', 'Unknown')}")
        print(f"   👤 Name: {user_info.get('name', 'Unknown')}")
        print(f"   🆔 User ID: {user_info.get('id', 'Unknown')}")
        print(f"   🔑 Client ID: {creds.client_id}")
        
        # Update settings with the actual email
        email_address = user_info.get('emailAddress')
        if email_address:
            print(f"\n💡 This account ({email_address}) will now be used for sending emails!")
            print(f"   Update your .env file with: DEFAULT_FROM_EMAIL={email_address}")
        
        return email_address
        
    except Exception as e:
        print(f"❌ Error getting OAuth2 account info: {str(e)}")
        return None

if __name__ == "__main__":
    get_oauth2_account_info()
