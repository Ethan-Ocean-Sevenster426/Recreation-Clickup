#!/bin/bash

# SSL Certificate Setup Script for eclick.co.za
# This script sets up SSL certificates using Let's Encrypt

set -e

echo "🔒 Setting up SSL certificates for eclick.co.za..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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
   print_error "This script should not be run as root"
   exit 1
fi

# Check if domain resolves to this server
print_status "Checking if eclick.co.za resolves to this server..."
SERVER_IP=$(curl -s ifconfig.me)
DOMAIN_IP=$(dig +short eclick.co.za | tail -n1)

if [ "$SERVER_IP" != "$DOMAIN_IP" ]; then
    print_error "Domain eclick.co.za ($DOMAIN_IP) does not resolve to this server ($SERVER_IP)"
    print_error "Please update your DNS records first"
    exit 1
fi

print_status "Domain resolution check passed ✓"

# Install certbot if not already installed
if ! command -v certbot &> /dev/null; then
    print_status "Installing certbot..."
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
fi

# Stop nginx temporarily for certificate generation
print_status "Stopping nginx for certificate generation..."
sudo systemctl stop nginx

# Generate SSL certificate
print_status "Generating SSL certificate for eclick.co.za and www.eclick.co.za..."
sudo certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email admin@eclick.co.za \
    -d eclick.co.za \
    -d www.eclick.co.za

# Update nginx configuration to use the generated certificates
print_status "Updating nginx configuration with SSL certificates..."
sudo sed -i 's|ssl_certificate /etc/ssl/certs/eclick.co.za.crt;|ssl_certificate /etc/letsencrypt/live/eclick.co.za/fullchain.pem;|' /etc/nginx/sites-available/eclick
sudo sed -i 's|ssl_certificate_key /etc/ssl/private/eclick.co.za.key;|ssl_certificate_key /etc/letsencrypt/live/eclick.co.za/privkey.pem;|' /etc/nginx/sites-available/eclick

# Test nginx configuration
print_status "Testing nginx configuration..."
sudo nginx -t

# Start nginx
print_status "Starting nginx with SSL configuration..."
sudo systemctl start nginx
sudo systemctl enable nginx

# Set up automatic certificate renewal
print_status "Setting up automatic certificate renewal..."
sudo crontab -l 2>/dev/null | grep -v certbot || true | sudo crontab -
echo "0 12 * * * /usr/bin/certbot renew --quiet --post-hook 'systemctl reload nginx'" | sudo crontab -

# Test SSL certificate
print_status "Testing SSL certificate..."
sleep 5  # Wait for nginx to start
if curl -s -I https://eclick.co.za | grep -q "200 OK"; then
    print_status "SSL certificate is working correctly ✓"
else
    print_warning "SSL certificate test failed. Please check nginx logs."
fi

# Show certificate information
print_status "Certificate information:"
sudo certbot certificates

print_status "🎉 SSL setup completed successfully!"
print_status "Your site is now available at:"
echo "  - https://eclick.co.za"
echo "  - https://www.eclick.co.za"
echo ""
print_status "Certificate will auto-renew every 90 days"
print_status "You can test SSL configuration at: https://www.ssllabs.com/ssltest/analyze.html?d=eclick.co.za"
