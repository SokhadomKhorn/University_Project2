#!/usr/bin/env bash
# ==============================================================================
# EC2 Instance 3: User Microservice (Port 5004)
# Usage:
#   ./run-ec2-3.sh [MONGO_URI]
# Example:
#   ./run-ec2-3.sh "mongodb://<EC2_1_IP>:27017/university_identity_db"
# ==============================================================================

MONGO_URI=${1:-${MONGO_URI:-"mongodb://172.31.9.169:27017/university_identity_db"}}

if [ -n "$MONGO_URI" ]; then
    export MONGO_URI="$MONGO_URI"
fi

echo "=========================================================================="
echo " Starting User Microservice on EC2 Instance 3"
echo " - User Microservice Port  : 5004"
echo " - Mongo URI               : ${MONGO_URI:-'Default Localhost'}"
echo "=========================================================================="

# Stop any previous instances
pm2 stop user-service 2>/dev/null || true
pm2 delete user-service 2>/dev/null || true

# Start User Microservice
cd User_Microservice && pm2 start index.js --name "user-service"
cd ..

pm2 status
echo ""
echo "User Microservice is running! Use 'pm2 logs user-service' to view logs."
