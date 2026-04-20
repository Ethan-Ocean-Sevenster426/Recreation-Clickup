# Django E-Click Deployment Guide for Ubuntu Server

## Server Information
- **IP Address**: 167.88.43.168
- **Port**: 1204
- **Server Type**: Hostinger Ubuntu

## Prerequisites
Make sure your Ubuntu server has:
- Python 3.8+
- Git
- Nginx (optional, for reverse proxy)
- SQL Server (if using SQL Server database)

## Quick Deployment

### Option 1: Shell Script (Recommended)
```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
sudo bash deploy.sh
```

### Option 2: Python Script
```bash
# Make script executable
chmod +x deploy_simple.py

# Run deployment
sudo python3 deploy_simple.py
```

## Manual Deployment Steps

### 1. Connect to Server
```bash
ssh root@167.88.43.168
```

### 2. Install Dependencies
```bash
# Update system
apt update && apt upgrade -y

# Install Python and Git
apt install -y python3 python3-pip python3-venv git nginx

# Install SQL Server dependencies (if using SQL Server)
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt update
ACCEPT_EULA=Y apt install -y msodbcsql18
```

### 3. Setup Project Directory
```bash
mkdir -p /var/www/eclick
cd /var/www/eclick
git clone https://github.com/MOCDATA-PTY/Django-E-Click.git .
```

### 4. Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.production.txt
```

### 5. Configure Environment
```bash
# Copy and edit environment file
cp env.production .env
nano .env

# Update with your actual values:
# - SECRET_KEY (generate a strong one)
# - Database credentials
# - Email settings
```

### 6. Django Setup
```bash
# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 7. Start Application
```bash
# Start Gunicorn on port 1204
gunicorn --bind 0.0.0.0:1204 --daemon eclick_project.wsgi:application
```

## Configuration Files

### Nginx Configuration
Copy `nginx.conf` to `/etc/nginx/sites-available/eclick` and enable:
```bash
cp nginx.conf /etc/nginx/sites-available/eclick
ln -s /etc/nginx/sites-available/eclick /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Systemd Service
Copy `eclick.service` to `/etc/systemd/system/` and enable:
```bash
cp eclick.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable eclick
systemctl start eclick
```

## Environment Variables

Create a `.env` file in your project directory:
```bash
DEBUG=False
SECRET_KEY=your-super-secret-key-here

# Database (SQL Server)
DB_ENGINE=mssql
DB_NAME=eclick_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=1433
DB_DRIVER=ODBC Driver 18 for SQL Server

# Email (Gmail)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

## Database Setup

### SQL Server
1. Install SQL Server on Ubuntu
2. Create database: `eclick_db`
3. Create user with appropriate permissions
4. Update `.env` file with credentials

### SQLite (Development)
For development, the app will use SQLite by default.

## Security Considerations

1. **Firewall**: Configure UFW to only allow necessary ports
2. **SSL**: Set up Let's Encrypt for HTTPS
3. **Secret Key**: Use a strong, unique SECRET_KEY
4. **Database**: Use strong passwords and limit access
5. **Updates**: Keep system and packages updated

## Monitoring and Logs

### Check Application Status
```bash
# Check if running on port 1204
netstat -tlnp | grep 1204

# Check Gunicorn processes
ps aux | grep gunicorn

# Check logs
tail -f /var/log/gunicorn/access.log
tail -f /var/log/gunicorn/error.log
```

### Health Check
The application includes a health check endpoint:
```
http://167.88.43.168:1204/health/
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Use `lsof -ti:1204 | xargs kill -9`
2. **Permission denied**: Check file ownership with `chown -R www-data:www-data /var/www/eclick`
3. **Database connection**: Verify SQL Server is running and credentials are correct
4. **Static files**: Run `python manage.py collectstatic --noinput`

### Logs
- Application logs: Check Gunicorn output
- System logs: `journalctl -u eclick`
- Nginx logs: `/var/log/nginx/`

## Updates

To update the application:
```bash
cd /var/www/eclick
git pull origin master
source venv/bin/activate
pip install -r requirements.production.txt
python manage.py collectstatic --noinput
python manage.py migrate
systemctl restart eclick
```

## Support

For issues or questions, check:
1. Django logs and error messages
2. System logs
3. Network connectivity
4. Database connectivity
5. File permissions
