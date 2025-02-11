# import multiprocessing
import os

# Socket binding
bind = 'unix:/var/www/api/run/gunicorn.sock'

# Dynamic worker count based on CPU cores
workers = 4  # Adjust or leave static as needed
# workers = multiprocessing.cpu_count() * 2 + 1  # Adjust or leave static as needed

# Timeout settings
timeout = 300

# Worker class for ASGI applications
worker_class = 'uvicorn.workers.UvicornWorker'

# Log settings
loglevel = 'info'
log_dir = '/var/www/api/logs'
accesslog = os.path.join(log_dir, 'gunicorn_access.log')
errorlog = os.path.join(log_dir, 'gunicorn_error.log')

# Create log directory if it doesn't exist
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Keep-alive settings
keepalive = 5

# Preloading application
# preload_app = True

def on_starting(server):
    """Set up worker ID tracking"""
    server.worker_id = 0

def post_fork(server, worker):
    """Assign unique ID to each worker"""
    worker.worker_id = server.worker_id
    server.worker_id += 1
    os.environ["WORKER_ID"] = str(worker.worker_id)

def when_ready(server):
    server.log.info("Gunicorn is ready to receive requests.")

def on_exit(server):
    server.log.info("Gunicorn is shutting down.")
