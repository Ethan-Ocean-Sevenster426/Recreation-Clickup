# Google Cloud Email Integration Setup

This guide will help you set up Google Cloud API to send emails from your Gmail account using the E-Click Django project.

## Prerequisites

1. A Google account
2. Access to Google Cloud Console
3. Python 3.7+ with pip installed

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note down your Project ID

## Step 2: Enable Gmail API

1. In your Google Cloud project, go to "APIs & Services" > "Library"
2. Search for "Gmail API"
3. Click on "Gmail API" and then click "Enable"

## Step 3: Create Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details:
   - Name: `eclick-email-service`
   - Description: `Service account for E-Click email functionality`
4. Click "Create and Continue"
5. Skip the optional steps and click "Done"

## Step 4: Create and Download Credentials

1. Click on the service account you just created
2. Go to the "Keys" tab
3. Click "Add Key" > "Create New Key"
4. Choose "JSON" format
5. Click "Create" - this will download a JSON file
6. Rename the downloaded file to `credentials.json`
7. Place the `credentials.json` file in the `home/` directory of your Django project

## Step 5: Configure Gmail API Permissions

1. Go to your Gmail account settings
2. Enable "Less secure app access" (for testing) or set up OAuth2 properly
3. If using a service account, you'll need to delegate domain-wide authority:
   - Go to Google Workspace Admin Console
   - Navigate to Security > API Controls
   - Add your service account email to the list of authorized APIs

## Step 6: Update Django Settings

Edit `eclick/settings.py` and update the email configuration:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Replace with your Gmail address
EMAIL_HOST_PASSWORD = 'your-app-password'  # Replace with your Gmail app password
DEFAULT_FROM_EMAIL = 'noreply@eclick.com'

# Google Cloud API Configuration
GOOGLE_CLOUD_API_KEY = 'AIzaSyBAHeuA83Rl--GvorBIZlY8UOratOu-X2U'
```

## Step 7: Install Required Packages

Run the following command to install the required Google Cloud libraries:

```bash
pip install google-cloud-storage google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Step 8: Test the Integration

1. Start your Django development server:
   ```bash
   python manage.py runserver
   ```

2. Log in to your Django admin account

3. Navigate to "Test Email" in the sidebar

4. Enter a test email address and click "Send Test Email"

## Troubleshooting

### Common Issues

1. **"Gmail API requires OAuth2 authentication"**
   - Make sure you have the `credentials.json` file in the `home/` directory
   - Verify the credentials file is properly formatted

2. **"Invalid credentials"**
   - Check that your service account has the correct permissions
   - Ensure the Gmail API is enabled in your Google Cloud project

3. **"Permission denied"**
   - Make sure your Gmail account allows less secure app access
   - Or properly configure OAuth2 with domain-wide delegation

### Alternative Setup (Simpler)

If you prefer a simpler setup using SMTP instead of Gmail API:

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security > 2-Step Verification > App passwords
   - Generate a password for "Mail"
3. Use the app password in your Django settings

## File Structure

After setup, your project should have this structure:

```
E-Click Django Website/
├── home/
│   ├── credentials.json          # Your OAuth2 credentials
│   ├── credentials_template.json # Template file
│   ├── services.py              # Email service
│   └── ...
├── eclick/
│   └── settings.py              # Updated with email config
└── GOOGLE_CLOUD_EMAIL_SETUP.md  # This file
```

## Security Notes

1. **Never commit credentials to version control**
   - Add `credentials.json` to your `.gitignore` file
   - Use environment variables for sensitive data in production

2. **Use environment variables in production**
   ```python
   import os
   
   EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
   EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
   ```

3. **Regular credential rotation**
   - Rotate your service account keys regularly
   - Monitor API usage in Google Cloud Console

## API Usage Limits

- Gmail API has daily quotas
- Monitor usage in Google Cloud Console
- Consider implementing rate limiting for production use

## Support

If you encounter issues:

1. Check the Django logs for error messages
2. Verify your Google Cloud project settings
3. Test with the provided test email functionality
4. Review Google Cloud Console for API usage and errors

## Next Steps

Once the basic email functionality is working:

1. Customize email templates in `home/services.py`
2. Add attachment support for reports
3. Implement email scheduling
4. Add email tracking and analytics
5. Set up email templates for different report types 