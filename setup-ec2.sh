#!/usr/bin/env bash
# ==============================================================================
# AWS EC2 Configuration Script for Project 2 Microservices
# Compatible with Ubuntu 20.04 / 22.04 / 24.04 LTS
# ==============================================================================

set -e

echo "========================================================================"
echo " Starting EC2 Instance Configuration (Task 1)"
echo "========================================================================"

# Step 1: Update & Upgrade Ubuntu OS packages
echo ">>> [1/4] Updating and upgrading system packages..."
sudo apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

# Step 2: Check & Install Git
echo ">>> [2/4] Checking Git installation..."
if ! command -v git &> /dev/null; then
    echo "Git not found. Installing git..."
    sudo apt-get install -y git
else
    echo "Git is already installed: $(git --version)"
fi

# Step 3: Install Node.js (v20 LTS) and npm
echo ">>> [3/4] Checking Node.js and npm..."
if ! command -v node &> /dev/null; then
    echo "Installing Node.js 20 LTS via NodeSource..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo "Node.js is already installed: $(node --version)"
fi

# Step 4: Install PM2 process manager for background service management
echo ">>> [4/4] Installing PM2 globally for reliable microservice hosting..."
sudo npm install -g pm2

# Optional Step: Check if local MongoDB installation is requested on EC2 Instance 1
if [ "$1" == "--install-mongo" ]; then
    echo ">>> Installing MongoDB Community Edition on this instance..."
    sudo apt-get install -y gnupg curl
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
        sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor --yes
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/7.0 multiverse" | \
        sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
    sudo apt-get update -y
    sudo apt-get install -y mongodb-org
    # Allow external connections on port 27017 for EC2 instances
    sudo sed -i 's/bindIp: 127.0.0.1/bindIp: 0.0.0.0/' /etc/mongod.conf
    sudo systemctl daemon-reload
    sudo systemctl start mongod
    sudo systemctl enable mongod
    echo "MongoDB installed and started on port 27017 (bind: 0.0.0.0)!"
fi

echo "========================================================================"
echo " Configuration Complete!"
echo " Node.js : $(node -v)"
echo " npm     : $(npm -v)"
echo " Git     : $(git --version)"
echo " PM2     : $(pm2 -v)"
echo "========================================================================"
