#!/usr/bin/env bash
# ==============================================================================
# EC2 Instance 1: API Gateway (Port 4000) + Registration (5001) + Login (5002)
# Usage:
#   ./run-ec2-1.sh <EC2_2_IP> <EC2_3_IP> [MONGO_URI]
# Example:
#   ./run-ec2-1.sh 54.210.10.20 54.210.10.30
# ==============================================================================

EC2_2_IP=${1:-${EC2_2_IP:-"172.31.3.233"}}
EC2_3_IP=${2:-${EC2_3_IP:-"172.31.2.148"}}
MONGO_URI=${3:-${MONGO_URI:-"mongodb://127.0.0.1:27017/university_identity_db"}}

export ADMIN_SERVICE="http://${EC2_2_IP}:5003"
export USER_SERVICE="http://${EC2_3_IP}:5004"
export REGISTRATION_SERVICE="http://localhost:5001"
export LOGIN_SERVICE="http://localhost:5002"

if [ -n "$MONGO_URI" ]; then
    export MONGO_URI="$MONGO_URI"
fi

echo "=========================================================================="
echo " Starting Services on EC2 Instance 1"
echo " - API Gateway              : Port 4000"
echo " - Registration Microservice: Port 5001 (Local)"
echo " - Login Microservice       : Port 5002 (Local)"
echo " - Admin Target             : $ADMIN_SERVICE"
echo " - User Target              : $USER_SERVICE"
echo "=========================================================================="

# Stop any previous instances
pm2 stop all 2>/dev/null || true
pm2 delete all 2>/dev/null || true

# Start microservices with PM2
cd Registration_Microservice && pm2 start index.js --name "registration-service"
cd ../Login_Microservice && pm2 start index.js --name "login-service"
cd ../APIGateway_Microservice && pm2 start index.js --name "api-gateway"
cd ..

pm2 status
echo ""
echo "All 3 services are running in background! Use 'pm2 logs' to view logs."
