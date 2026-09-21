# 🚀 Project 2: Multi-Instance EC2 Microservices Deployment Guide
## Complete Step-by-Step Instructions & Screenshot Submission Guide

---

## 📌 Architecture Overview

| EC2 Instance | OS | Hosted Microservices | Default Ports | Public IP |
|---|---|---|---|---|
| **EC2 Instance 1** | Ubuntu 22.04 LTS | **API Gateway**, **Registration**, **Login** | `4000`, `5001`, `5002` | `[EC2_1_PUBLIC_IP]` |
| **EC2 Instance 2** | Ubuntu 22.04 LTS | **Admin Microservice** | `5003` | `[EC2_2_PUBLIC_IP]` |
| **EC2 Instance 3** | Ubuntu 22.04 LTS | **User Microservice** | `5004` | `[EC2_3_PUBLIC_IP]` |

---

## 🔐 AWS Security Group Configuration (Crucial Step!)

To allow communication between EC2 instances and from your Postman client, make sure your EC2 Security Group Inbound Rules include:

| Type | Port Range | Source | Purpose |
|---|---|---|---|
| **SSH** | `22` | `0.0.0.0/0` (or My IP) | SSH access to EC2 instances |
| **Custom TCP** | `4000` | `0.0.0.0/0` | API Gateway access from Postman |
| **Custom TCP** | `5001` - `5004` | `0.0.0.0/0` (or VPC CIDR) | Microservices communication |
| **Custom TCP** | `27017` | `0.0.0.0/0` (or VPC CIDR) | MongoDB connection (if hosted on EC2 #1) |

---

## 🛠️ Task 1: Setup & Configure All 3 EC2 Instances

Once you launch your 3 Ubuntu EC2 instances:

### 1. Connect to each EC2 instance via SSH:
```bash
# Instance 1
ssh -i "path/to/labsuser.pem" ubuntu@<EC2_1_PUBLIC_IP>

# Instance 2
ssh -i "path/to/labsuser.pem" ubuntu@<EC2_2_PUBLIC_IP>

# Instance 3
ssh -i "path/to/labsuser.pem" ubuntu@<EC2_3_PUBLIC_IP>
```

### 2. Run the Automated Configuration Script (`setup-ec2.sh`):
You can run this one-liner directly on each instance:
```bash
curl -sSL https://raw.githubusercontent.com/<YOUR_GITHUB_USER>/<YOUR_REPO>/main/setup-ec2.sh | bash
```
*Or clone the repo first and run:*
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd University_Project-main
chmod +x setup-ec2.sh
./setup-ec2.sh
```

This script automatically:
1. Updates and upgrades Ubuntu OS (`apt-get update && apt-get upgrade -y`).
2. Checks Git and installs it if missing.
3. Installs Node.js (v20 LTS), npm, and PM2 process manager.

---

## 📸 Task 2: Screenshot the 3 EC2 Instances Public IPs

1. Open AWS Management Console > **EC2 Dashboard** > **Instances**.
2. Capture screenshots showing:
   - **Screenshot 1**: EC2 Instance 1 Public IPv4 address.
   - **Screenshot 2**: EC2 Instance 2 Public IPv4 address.
   - **Screenshot 3**: EC2 Instance 3 Public IPv4 address.
3. Save them in the `screenshots/` directory as:
   - `screenshots/task2_ec2_1_ip.png`
   - `screenshots/task2_ec2_2_ip.png`
   - `screenshots/task2_ec2_3_ip.png`

---

## 🚀 Task 3 & 4: Start Microservices & Update GitHub

### On EC2 Instance 1 (API Gateway + Registration + Login):
```bash
cd University_Project-main
# Run with the Public/Private IPs of Instance 2 and 3:
chmod +x run-ec2-1.sh
./run-ec2-1.sh <EC2_2_IP> <EC2_3_IP> [OPTIONAL_MONGO_URI]
```

### On EC2 Instance 2 (Admin Microservice):
```bash
cd University_Project-main
chmod +x run-ec2-2.sh
./run-ec2-2.sh [OPTIONAL_MONGO_URI]
```

### On EC2 Instance 3 (User Microservice):
```bash
cd University_Project-main
chmod +x run-ec2-3.sh
./run-ec2-3.sh [OPTIONAL_MONGO_URI]
```

---

## 🧪 Tasks 5 to 8: Postman Execution & Screenshot Checklist

Import `Project2_EC2_MultiInstance_Postman_Collection.json` into Postman.
Set collection variable `gateway_url` to:
`http://<EC2_1_PUBLIC_IP>:4000`

### Postman Test Suite & Required Screenshots:

| Task | Action & Endpoint | Expected Result | Screenshot Name |
|---|---|---|---|
| **Task 5.1** | `POST {{gateway_url}}/register/userregister` (New User) | `201 Created` + User Object | `task5_1_add_record_postman.png` & `task5_1_mongodb.png` |
| **Task 5.2** | `POST {{gateway_url}}/register/userregister` (Same Email) | `400 Bad Request` (Email exists) | `task5_2_duplicate_email.png` |
| **Task 6.1** | `POST {{gateway_url}}/auth/login` (Admin role) | `200 OK` + JWT Token | `task6_1_admin_login_jwt.png` |
| **Task 6.2** | `POST {{gateway_url}}/auth/login` (User role) | `200 OK` + JWT Token | `task6_2_user_login_jwt.png` |
| **Task 7.1** | `GET {{gateway_url}}/admin/viewalluser` (Admin JWT) | `200 OK` + List of all users | `task7_1_admin_viewalluser.png` |
| **Task 7.2** | `PUT {{gateway_url}}/user/updateprofile` (User JWT) | `200 OK` + Updated User Profile | `task7_2_user_updateprofile.png` |
| **Task 8.1** | `PUT {{gateway_url}}/user/updateprofile` (Admin JWT) | `403 Forbidden` (RBAC Denied) | `task8_1_admin_call_user_api.png` |
| **Task 8.2** | `GET {{gateway_url}}/admin/viewalluser` (User JWT) | `403 Forbidden` (RBAC Denied) | `task8_2_user_call_admin_api.png` |

---

## 📄 Automated Word Document & Single PDF Creation

Whenever your screenshots are saved in the `screenshots/` directory, simply run:
```bash
python generate_submission_doc.py
```
This automatically produces:
1. **`Project2_Submission.docx`** (Complete Word Document with student info, tables, descriptions, and all embedded screenshots)
2. **`Project2_Submission.pdf`** (Single converted PDF ready to upload to Canvas!)
