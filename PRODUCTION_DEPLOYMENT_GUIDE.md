# Django E-Click Production Deployment Guide

## 🚀 Ubuntu Hosting Setup for eclick.co.za

This guide ensures your Django project is ready for production deployment on Ubuntu with HTTPS, Gunicorn, and Nginx.

## 📋 Pre-Deployment Checklist

### ✅ Requirements Verified
- [x] Updated `requirements.production.txt` with all dependencies
- [x] Created production settings (`eclick/settings_production.py`)
- [x] Configured HTTPS settings for eclick.co.za domain
- [x] Updated WSGI configuration
- [x] Created Nginx configuration for HTTPS
- [x] Updated Gunicorn configuration
- [x] Created deployment scripts

### 🔧 Configuration Files Created
- `eclick/settings_production.py` - Production Django settings
- `nginx.conf` - HTTPS Nginx configuration
- `gunicorn.conf.py` - Production Gunicorn settings
- `deploy_ubuntu.sh` - Automated deployment script
- `setup_ssl.sh` - SSL certificate setup script
- `env.production.template` - Environment variables template

## 🛠️ Deployment Steps

### 1. Server Preparation
```bash
# Make deployment script executable
chmod +x deploy_ubuntu.sh

# Run deployment script
./deploy_ubuntu.sh
```

### 2. SSL Certificate Setup
```bash
# Make SSL setup script executable
chmod +x setup_ssl.sh

# Run SSL setup
./setup_ssl.sh
```

### 3. Environment Configuration
```bash
# Copy and edit environment file
cp env.production.template .env
nano .env  # Update with your actual values
```

## 🔒 Security Features Implemented

### HTTPS Configuration
- ✅ HTTP to HTTPS redirect
- ✅ SSL/TLS 1.2 and 1.3 support
- ✅ Secure cipher suites
- ✅ HSTS headers
- ✅ Secure session cookies
- ✅ CSRF protection with trusted origins

### Security Headers
- ✅ Strict-Transport-Security
- ✅ X-Frame-Options
- ✅ X-XSS-Protection
- ✅ X-Content-Type-Options
- ✅ Referrer-Policy
- ✅ Content-Security-Policy

### Django Security Settings
- ✅ DEBUG = False
- ✅ SECRET_KEY from environment
- ✅ Allowed hosts restricted to domain
- ✅ Secure session settings
- ✅ CSRF cookie security

## 📁 File Structure After Deployment

```
/var/www/eclick/
├── venv/                    # Python virtual environment
├── logs/                    # Application logs
│   ├── django.log
│   ├── gunicorn_access.log
│   └── gunicorn_error.log
├── media/                   # User uploaded files
├── staticfiles/            # Collected static files
├── .env                    # Environment variables
├── manage.py
├── eclick/
│   ├── settings_production.py
│   └── wsgi.py
└── requirements.production.txt
```

## 🔍 Troubleshooting Common Issues

### Internal Server Error 500

#### 1. Check Django Logs
```bash
sudo tail -f /var/www/eclick/logs/django.log
```

#### 2. Check Gunicorn Logs
```bash
sudo tail -f /var/www/eclick/logs/gunicorn_error.log
```

#### 3. Check Nginx Logs
```bash
sudo tail -f /var/log/nginx/error.log
```

#### 4. Common Causes and Solutions

**Missing Dependencies:**
```bash
cd /var/www/eclick
source venv/bin/activate
pip install -r requirements.production.txt
```

**Database Connection Issues:**
```bash
# Test database connection
python manage.py dbshell --settings=eclick.settings_production
```

**Static Files Not Found:**
```bash
python manage.py collectstatic --noinput --settings=eclick.settings_production
```

**Permission Issues:**
```bash
sudo chown -R www-data:www-data /var/www/eclick
sudo chmod -R 755 /var/www/eclick
sudo chmod -R 775 /var/www/eclick/media
sudo chmod -R 775 /var/www/eclick/logs
```

**Missing Environment Variables:**
```bash
# Check if .env file exists and has correct values
cat .env
```

### Service Management

#### Restart Services
```bash
# Restart Django application
sudo supervisorctl restart eclick

# Restart Nginx
sudo systemctl restart nginx

# Check service status
sudo supervisorctl status eclick
sudo systemctl status nginx
```

#### View Service Logs
```bash
# Django logs
sudo tail -f /var/www/eclick/logs/django.log

# Gunicorn logs
sudo tail -f /var/www/eclick/logs/gunicorn_error.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🔄 Maintenance Commands

### Database Operations
```bash
cd /var/www/eclick
source venv/bin/activate

# Run migrations
python manage.py migrate --settings=eclick.settings_production

# Create superuser
python manage.py createsuperuser --settings=eclick.settings_production

# Database shell
python manage.py dbshell --settings=eclick.settings_production
```

### Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput --settings=eclick.settings_production

# Clear cache
python manage.py clear_cache --settings=eclick.settings_production
```

### SSL Certificate Renewal
```bash
# Manual renewal
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

## 📊 Monitoring and Performance

### Health Check
```bash
# Test application health
curl -I https://eclick.co.za/health/

# Test SSL certificate
curl -I https://eclick.co.za
```

### Performance Monitoring
```bash
# Check system resources
htop
df -h
free -h

# Check application processes
ps aux | grep gunicorn
ps aux | grep nginx
```

## 🚨 Emergency Procedures

### Quick Rollback
```bash
# Stop services
sudo supervisorctl stop eclick
sudo systemctl stop nginx

# Restore from backup (if available)
# ... restore procedure ...

# Restart services
sudo systemctl start nginx
sudo supervisorctl start eclick
```

### Emergency Access
```bash
# Access Django shell
cd /var/www/eclick
source venv/bin/activate
python manage.py shell --settings=eclick.settings_production
```

## 📞 Support Information

- **Domain:** eclick.co.za
- **Server IP:** Check with `curl ifconfig.me`
- **SSL Certificate:** Let's Encrypt (auto-renewal configured)
- **Log Location:** `/var/www/eclick/logs/`
- **Configuration:** `/etc/nginx/sites-available/eclick`

## ✅ Final Verification

After deployment, verify:
1. ✅ Site loads at https://eclick.co.za
2. ✅ HTTP redirects to HTTPS
3. ✅ SSL certificate is valid
4. ✅ Static files load correctly
5. ✅ Database connections work
6. ✅ Email functionality works
7. ✅ Admin panel accessible
8. ✅ No 500 errors in logs

Your Django E-Click project is now ready for production hosting on Ubuntu with HTTPS!
