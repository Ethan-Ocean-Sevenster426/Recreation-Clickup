#!/bin/bash

# Ubuntu Deployment Script for Django E-Click Project
# This script sets up the project for production deployment on Ubuntu

set -e  # Exit on any error

echo "🚀 Starting Django E-Click Project Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
print_status "Installing required system packages..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    mysql-client \
    libmysqlclient-dev \
    pkg-config \
    nginx \
    supervisor \
    git \
    curl \
    wget \
    build-essential \
    certbot \
    python3-certbot-nginx \
    ufw

# Install Node.js (for any frontend dependencies)
print_status "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Create project directory
PROJECT_DIR="/var/www/eclick"
print_status "Creating project directory at $PROJECT_DIR..."
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR

# Copy project files (assuming we're running from project root)
print_status "Copying project files..."
cp -r . $PROJECT_DIR/
cd $PROJECT_DIR

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.production.txt

# Create logs directory
print_status "Creating logs directory..."
mkdir -p logs
touch logs/django.log
chmod 664 logs/django.log

# Create media directory
print_status "Creating media directory..."
mkdir -p media
chmod 755 media

# Set up environment file
print_status "Setting up environment configuration..."
if [ ! -f .env ]; then
    cp env.production.template .env
    print_warning "Please edit .env file with your actual configuration values"
fi

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput --settings=eclick.settings_production

# Run database migrations
print_status "Running database migrations..."
python manage.py migrate --settings=eclick.settings_production

# Create superuser (optional)
print_warning "Do you want to create a superuser? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser --settings=eclick.settings_production
fi

# Set proper permissions
print_status "Setting proper permissions..."
sudo chown -R www-data:www-data $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR
sudo chmod -R 775 $PROJECT_DIR/media
sudo chmod -R 775 $PROJECT_DIR/logs

# Configure Gunicorn
print_status "Configuring Gunicorn..."
sudo cp gunicorn.conf.py /etc/gunicorn.d/eclick.conf

# Configure Nginx
print_status "Configuring Nginx..."
sudo cp nginx.conf /etc/nginx/sites-available/eclick
sudo ln -sf /etc/nginx/sites-available/eclick /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
print_status "Testing Nginx configuration..."
sudo nginx -t

# Configure firewall
print_status "Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Set up SSL certificate with Let's Encrypt
print_status "Setting up SSL certificate..."
print_warning "Make sure your domain eclick.co.za points to this server's IP address"
print_warning "You can get SSL certificate with: sudo certbot --nginx -d eclick.co.za -d www.eclick.co.za"

# Configure Supervisor
print_status "Configuring Supervisor..."
sudo tee /etc/supervisor/conf.d/eclick.conf > /dev/null <<EOF
[program:eclick]
command=$PROJECT_DIR/venv/bin/gunicorn --config $PROJECT_DIR/gunicorn.conf.py eclick.wsgi:application
directory=$PROJECT_DIR
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$PROJECT_DIR/logs/gunicorn.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
EOF

# Reload Supervisor configuration
sudo supervisorctl reread
sudo supervisorctl update

# Start services
print_status "Starting services..."
sudo systemctl restart nginx
sudo supervisorctl restart eclick

# Enable services to start on boot
sudo systemctl enable nginx
sudo systemctl enable supervisor

# Check service status
print_status "Checking service status..."
sudo systemctl status nginx --no-pager -l
sudo supervisorctl status eclick

print_status "🎉 Deployment completed successfully!"
print_status "Your Django application should now be running on HTTPS (eclick.co.za)"
print_warning "IMPORTANT: Complete these steps:"
print_warning "1. Edit .env file with your actual configuration"
print_warning "2. Get SSL certificate: sudo certbot --nginx -d eclick.co.za -d www.eclick.co.za"
print_warning "3. Test your site: https://eclick.co.za"
print_warning "4. Set up database backups"
print_warning "5. Configure monitoring and log rotation"

echo ""
print_status "Useful commands:"
echo "  Check logs: sudo tail -f $PROJECT_DIR/logs/django.log"
echo "  Restart app: sudo supervisorctl restart eclick"
echo "  Check status: sudo supervisorctl status eclick"
echo "  Reload nginx: sudo systemctl reload nginx"
