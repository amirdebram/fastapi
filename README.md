# fastapi
Boilerplate Code to get started with fastapi

# Install Redis Server
# Ubuntu
sudo apt-get install lsb-release curl gpg
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
sudo chmod 644 /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
sudo apt-get update
sudo apt-get install redis
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Redhat
sudo yum install redis
sudo systemctl enable redis
sudo systemctl start redis

# Create a directory
/var/www/api

# Create a virtual environment
python3 -m venv .venv

# Install requirements
pip install -r /var/www/api/requirements.txt

# Generate your own secret key
https://djecrety.ir/

# Run project
cd /var/www/api
fastapi dev app/main.py
