#!/usr/bin/env bash
# ==============================================================================
# EC2 Instance 2: Admin Microservice (Port 5003)
# Usage:
#   ./run-ec2-2.sh [MONGO_URI]
# Example:
#   ./run-ec2-2.sh "mongodb://<EC2_1_IP>:27017/university_identity_db"
# ==============================================================================

MONGO_URI=${1:-${MONGO_URI:-"mongodb://172.31.9.169:27017/university_identity_db"}}

if [ -n "$MONGO_URI" ]; then
    export MONGO_URI="$MONGO_URI"
fi

echo "=========================================================================="
echo " Starting Admin Microservice on EC2 Instance 2"
echo " - Admin Microservice Port : 5003"
echo " - Mongo URI               : ${MONGO_URI:-'Default Localhost'}"
echo "=========================================================================="

# Stop any previous instances
pm2 stop admin-service 2>/dev/null || true
pm2 delete admin-service 2>/dev/null || true

# Start Admin Microservice
cd Admin_Microservice && pm2 start index.js --name "admin-service"
cd ..

pm2 status
echo ""
echo "Admin Microservice is running! Use 'pm2 logs admin-service' to view logs."
