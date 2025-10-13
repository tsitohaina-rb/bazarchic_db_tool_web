"""
Gunicorn configuration for production deployment
"""

import os
import multiprocessing

# Bind to PORT environment variable (Render requirement)
bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"

# Worker configuration
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000

# Timeout settings - increase for slow database connections
timeout = 120  # 2 minutes
graceful_timeout = 120
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'bazarchic_db_tool'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Preload app for better performance
preload_app = True

# Graceful restart on code changes (only in development)
reload = os.getenv('FLASK_ENV') == 'development'
