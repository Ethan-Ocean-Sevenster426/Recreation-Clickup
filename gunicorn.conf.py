# Gunicorn configuration file for production
import multiprocessing

# Server socket
bind = "unix:/var/www/luma/luma.sock"
backlog = 2048

# Worker processes
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging - use stdout/stderr so journalctl captures it
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "luma"

# Server mechanics
daemon = False
user = "www-data"
group = "www-data"
tmp_upload_dir = "/tmp"

# Worker process settings
preload_app = True
worker_tmp_dir = "/dev/shm"

# Security settings
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
