# Gunicorn configuration file for HTTPS production
import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"  # Only bind to localhost since Nginx will proxy
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/www/eclick/logs/gunicorn_access.log"
errorlog = "/var/www/eclick/logs/gunicorn_error.log"
loglevel = "info"

# Process naming
proc_name = "eclick"

# Server mechanics
daemon = False
pidfile = "/var/www/eclick/gunicorn.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = "/tmp"

# Worker process settings
preload_app = True
worker_tmp_dir = "/dev/shm"  # Use shared memory for better performance

# Security settings
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Environment variables
raw_env = [
    'DJANGO_SETTINGS_MODULE=eclick.settings_production',
]

# SSL settings (if running Gunicorn with SSL directly - not recommended with Nginx)
# keyfile = "/etc/ssl/private/eclick.co.za.key"
# certfile = "/etc/ssl/certs/eclick.co.za.crt"
