import os

# Define the content of the api.service file
service_content = """\
[Unit]
Description=Gunicorn instance to serve a FastAPI application
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/var/www/api/

# Set up the virtual environment's bin directory in the PATH
Environment="PATH=/var/www/api/.venv/bin:$PATH"
EnvironmentFile=/var/www/api/.env

# Environmentable variables
Environment="PATH=/var/www/api/.venv/bin"
Environment="SECRET_KEY=rb=bawvwn$gl#=48l#1%@e&np8skbi5780&ixj9a9-go)0kobe"
Environment="ALGORITHM=HS256"
Environment="SQLALCHEMY_DATABASE_URL=postgresql+asyncpg://username:password@localhost/database"

# Gunicorn Socket
ExecStart=/var/www/api/.venv/bin/gunicorn -c /var/www/api/run/gunicorn.py app.main:app

# Timeouts
TimeoutStartSec=30
TimeoutStopSec=30
Restart=on-failure
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""

# Define the file path
service_file_path = "/etc/systemd/system/api.service"

# Write the content to the file
with open(service_file_path, "w") as service_file:
    service_file.write(service_content)

# Set the file permissions to 644
os.chmod(service_file_path, 0o644)

print(f"Service file created at {service_file_path} with 644 permissions.")
