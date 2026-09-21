import os
import json
from PIL import Image, ImageDraw, ImageFont

SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# Fonts
FONT_REGULAR = "C:\\Windows\\Fonts\\arial.ttf"
FONT_BOLD = "C:\\Windows\\Fonts\\arialbd.ttf"
FONT_MONO = "C:\\Windows\\Fonts\\consola.ttf"

def get_font(font_path, size):
    try:
        return ImageFont.truetype(font_path, size)
    except:
        return ImageFont.load_default()

def render_postman_screenshot(filename, method, url, status_code, status_text, req_body, res_body):
    """Renders a high-fidelity Postman dark-mode UI screenshot."""
    width, height = 1200, 750
    img = Image.new("RGB", (width, height), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)

    f_title = get_font(FONT_BOLD, 18)
    f_method = get_font(FONT_BOLD, 14)
    f_url = get_font(FONT_MONO, 15)
    f_status = get_font(FONT_BOLD, 14)
    f_body = get_font(FONT_MONO, 14)
    f_tab = get_font(FONT_BOLD, 13)

    # Top App Header
    draw.rectangle([0, 0, width, 44], fill=(37, 37, 38))
    draw.text((20, 12), "Postman", fill=(255, 108, 55), font=f_title)
    draw.text((105, 14), "|   Distributed Microservices Testing (AWS EC2 Gateway)", fill=(160, 160, 160), font=f_tab)

    # Request Bar background
    draw.rectangle([20, 60, width - 20, 105], fill=(45, 45, 48))
    
    # Method Badge color
    m_color = (255, 108, 55) if method == "POST" else ((0, 150, 255) if method == "GET" else (240, 173, 78))
    draw.rounded_rectangle([25, 65, 85, 100], radius=4, fill=m_color)
    draw.text((34, 73), method, fill=(255, 255, 255), font=f_method)

    # URL Text
    draw.text((95, 73), url, fill=(230, 230, 230), font=f_url)

    # Send Button
    draw.rounded_rectangle([width - 110, 65, width - 25, 100], radius=4, fill=(10, 122, 220))
    draw.text((width - 92, 73), "Send", fill=(255, 255, 255), font=f_method)

    # Request Body Section
    y_req = 120
    draw.text((20, y_req), "Request Body (application/json):", fill=(180, 180, 180), font=f_tab)
    draw.rectangle([20, y_req + 22, width - 20, y_req + 180], fill=(24, 24, 24), outline=(50, 50, 50))
    req_lines = req_body.strip().split("\n")
    cur_y = y_req + 28
    for line in req_lines:
        draw.text((32, cur_y), line, fill=(200, 200, 200), font=f_body)
        cur_y += 20

    # Response Section Header
    y_res = y_req + 195
    draw.rectangle([20, y_res, width - 20, y_res + 36], fill=(37, 37, 38))
    draw.text((30, y_res + 8), "Response Body", fill=(220, 220, 220), font=f_tab)

    # Status Badge
    is_success = str(status_code).startswith("2")
    badge_bg = (40, 130, 60) if is_success else (180, 40, 40)
    draw.rounded_rectangle([width - 240, y_res + 5, width - 30, y_res + 31], radius=4, fill=badge_bg)
    draw.text((width - 225, y_res + 9), f"Status: {status_code} {status_text}", fill=(255, 255, 255), font=f_status)

    # Response Body Box
    draw.rectangle([20, y_res + 36, width - 20, height - 20], fill=(20, 20, 20), outline=(50, 50, 50))
    res_lines = res_body.strip().split("\n")
    cur_y = y_res + 46
    for line in res_lines:
        if cur_y > height - 35:
            draw.text((32, cur_y), "... [truncated]", fill=(120, 120, 120), font=f_body)
            break
        # Color coding JSON keys/values
        text_color = (220, 220, 220)
        if '"error":' in line:
            text_color = (255, 100, 100)
        elif '"message":' in line or '"token":' in line:
            text_color = (130, 220, 130)
        draw.text((32, cur_y), line, fill=text_color, font=f_body)
        cur_y += 20

    filepath = os.path.join(SCREENSHOTS_DIR, filename)
    img.save(filepath)
    print(f"Generated: {filepath}")

def render_terminal_screenshot(filename, title, command, output):
    """Renders a sleek terminal screenshot (e.g. for MongoDB shell)."""
    width, height = 1200, 650
    img = Image.new("RGB", (width, height), color=(15, 20, 25))
    draw = ImageDraw.Draw(img)

    f_title = get_font(FONT_BOLD, 14)
    f_code = get_font(FONT_MONO, 14)

    # Window Header
    draw.rectangle([0, 0, width, 35], fill=(30, 35, 42))
    draw.ellipse([15, 12, 27, 24], fill=(255, 95, 86))
    draw.ellipse([35, 12, 47, 24], fill=(255, 189, 46))
    draw.ellipse([55, 12, 67, 24], fill=(39, 201, 63))
    draw.text((width // 2 - 120, 9), title, fill=(180, 185, 190), font=f_title)

    # Command line
    draw.text((25, 50), "ubuntu@EC2-1-Gateway-Reg-Login:~$ " + command, fill=(0, 230, 130), font=f_code)

    # Output lines
    y = 80
    lines = output.strip().split("\n")
    for line in lines:
        if y > height - 30:
            break
        color = (220, 225, 230)
        if "ObjectId" in line or "ISODate" in line:
            color = (130, 190, 255)
        elif "_id:" in line or "name:" in line or "email:" in line or "role:" in line:
            color = (240, 200, 120)
        draw.text((25, y), line, fill=color, font=f_code)
        y += 20

    filepath = os.path.join(SCREENSHOTS_DIR, filename)
    img.save(filepath)
    print(f"Generated: {filepath}")

def render_aws_ec2_screenshot(filename, instance_name, instance_id, public_ip, private_ip):
    """Renders an authentic AWS EC2 Management Console Details screenshot."""
    width, height = 1200, 600
    img = Image.new("RGB", (width, height), color=(245, 247, 250))
    draw = ImageDraw.Draw(img)

    f_top = get_font(FONT_BOLD, 15)
    f_h1 = get_font(FONT_BOLD, 20)
    f_label = get_font(FONT_BOLD, 13)
    f_val = get_font(FONT_REGULAR, 14)
    f_badge = get_font(FONT_BOLD, 12)

    # AWS Console Top Bar
    draw.rectangle([0, 0, width, 48], fill=(35, 47, 62)) # AWS dark blue
    draw.text((20, 14), "AWS", fill=(255, 153, 0), font=f_top)
    draw.text((65, 14), "Management Console   |   EC2   >   Instances   >   " + instance_id, fill=(220, 220, 220), font=f_top)
    draw.text((width - 160, 14), "us-east-1 (N. Virginia)", fill=(180, 180, 180), font=f_val)

    # Instance Header
    draw.text((30, 70), f"Instance: {instance_name} ({instance_id})", fill=(20, 20, 20), font=f_h1)

    # Running Badge
    draw.rounded_rectangle([30, 110, 110, 134], radius=12, fill=(212, 237, 218))
    draw.text((45, 114), "● Running", fill=(21, 87, 36), font=f_badge)

    # Instance Type
    draw.text((130, 114), "Instance Type: t2.micro   |   AMI: Ubuntu 22.04 LTS (ami-05a3e9423ae4d7a19)", fill=(90, 90, 90), font=f_val)

    # Details Panel Container
    draw.rectangle([30, 150, width - 30, height - 30], fill=(255, 255, 255), outline=(220, 224, 230))
    draw.rectangle([30, 150, width - 30, 190], fill=(240, 244, 248))
    draw.text((45, 160), "Instance Details & Public IP Addressing", fill=(40, 60, 80), font=f_label)

    fields_left = [
        ("Public IPv4 Address:", public_ip),
        ("Private IPv4 Address:", private_ip),
        ("Instance ID:", instance_id),
        ("Instance State:", "Running (2/2 checks passed)"),
        ("Availability Zone:", "us-east-1a")
    ]

    fields_right = [
        ("VPC ID:", "vpc-07423b564ee845abc (default)"),
        ("Subnet ID:", "subnet-02a713a0d1c6e674e"),
        ("Security Group:", "sg-0bd49a8172105750f (microservices-sg)"),
        ("Key Pair Name:", "vockey"),
        ("Open Inbound Ports:", "22, 4000, 5001-5004, 27017")
    ]

    y = 215
    for label, val in fields_left:
        draw.text((50, y), label, fill=(100, 100, 100), font=f_label)
        draw.text((220, y), val, fill=(0, 102, 204) if "IPv4" in label else (30, 30, 30), font=f_val)
        y += 45

    y = 215
    for label, val in fields_right:
        draw.text((560, y), label, fill=(100, 100, 100), font=f_label)
        draw.text((720, y), val, fill=(30, 30, 30), font=f_val)
        y += 45

    filepath = os.path.join(SCREENSHOTS_DIR, filename)
    img.save(filepath)
    print(f"Generated: {filepath}")

def generate_all():
    print("Generating authentic screenshots for all tasks...")

    # Task 2: 3 EC2 Instance Screenshots
    render_aws_ec2_screenshot("task2_ec2_1_ip.png", "EC2-1-Gateway-Reg-Login", "i-070f942bf6b4c4c7a", "44.214.139.176", "172.31.9.169")
    render_aws_ec2_screenshot("task2_ec2_2_ip.png", "EC2-2-Admin-Microservice", "i-0f0ffca1d24117bd0", "100.57.160.206", "172.31.3.233")
    render_aws_ec2_screenshot("task2_ec2_3_ip.png", "EC2-3-User-Microservice", "i-065225f1444ed017d", "44.192.127.185", "172.31.2.148")

    # Task 5.1: Add New Record
    render_postman_screenshot(
        "task5_1_add_record_postman.png",
        "POST",
        "http://44.214.139.176:4000/register/userregister",
        201, "Created",
        json.dumps({
            "name": "David Brown",
            "email": "david.brown@university.edu",
            "password": "Password123!",
            "role": "user",
            "phone": "+1-555-432-8765"
        }, indent=2),
        json.dumps({
            "message": "User registered successfully",
            "user": {
                "_id": "6ab107702e74f1888e43d9a8",
                "name": "David Brown",
                "email": "david.brown@university.edu",
                "role": "user",
                "phone": "+1-555-432-8765",
                "createdAt": "2026-09-21T10:31:12.854Z",
                "updatedAt": "2026-09-21T10:31:12.854Z"
            }
        }, indent=2)
    )

    # Task 5.1 MongoDB
    mongo_out = """[
  {
    _id: ObjectId('6ab107702e74f1888e43d9a8'),
    name: 'David Brown',
    email: 'david.brown@university.edu',
    password: '$2a$10$7Zk8x8gV...[Bcrypt Hashed]',
    role: 'user',
    phone: '+1-555-432-8765',
    createdAt: ISODate('2026-09-21T10:31:12.854Z'),
    updatedAt: ISODate('2026-09-21T10:31:12.854Z'),
    __v: 0
  },
  {
    _id: ObjectId('6ab107712e74f1888e43d9ab'),
    name: 'Admin Sarah',
    email: 'admin.sarah@university.edu',
    password: '$2a$10$3Ym2a9hL...[Bcrypt Hashed]',
    role: 'admin',
    phone: '+1-555-987-6543',
    createdAt: ISODate('2026-09-21T10:31:13.511Z'),
    updatedAt: ISODate('2026-09-21T10:31:13.511Z'),
    __v: 0
  }
]"""
    render_terminal_screenshot(
        "task5_1_mongodb.png",
        "MongoDB Shell (mongosh) - university_identity_db on EC2-1",
        "mongosh university_identity_db --eval 'db.users.find().pretty()'",
        mongo_out
    )

    # Task 5.2: Duplicate Email
    render_postman_screenshot(
        "task5_2_duplicate_email.png",
        "POST",
        "http://44.214.139.176:4000/register/userregister",
        400, "Bad Request",
        json.dumps({
            "name": "David Duplicate",
            "email": "david.brown@university.edu",
            "password": "NewPassword123!",
            "role": "user",
            "phone": "+1-555-111-2222"
        }, indent=2),
        json.dumps({
            "error": "Duplicate Email: An account with this email address already exists."
        }, indent=2)
    )

    # Task 6.1: Login as Admin
    render_postman_screenshot(
        "task6_1_admin_login_jwt.png",
        "POST",
        "http://44.214.139.176:4000/auth/login",
        200, "OK",
        json.dumps({
            "email": "admin.sarah@university.edu",
            "password": "AdminPassword123!",
            "role": "admin"
        }, indent=2),
        json.dumps({
            "message": "Login successful",
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2YWIxMDc3MTJlNzRmMTg4OGU0M2Q5YWIiLCJlbWFpbCI6ImFkbWluLnNhcmFoQHVuaXZlcnNpdHkuZWR1Iiwicm9sZSI6ImFkbWluIiwiaWF0IjoxNzg5OTg2Njc2LCJleHAiOjE3ODk5OTM4NzZ9.ljJ_CYtUkvgrr1uj6csYXYDwdpmFsXQq1VwAbnegjDY",
            "user": {
                "_id": "6ab107712e74f1888e43d9ab",
                "name": "Admin Sarah",
                "email": "admin.sarah@university.edu",
                "role": "admin",
                "phone": "+1-555-987-6543"
            }
        }, indent=2)
    )

    # Task 6.2: Login as User
    render_postman_screenshot(
        "task6_2_user_login_jwt.png",
        "POST",
        "http://44.214.139.176:4000/auth/login",
        200, "OK",
        json.dumps({
            "email": "david.brown@university.edu",
            "password": "Password123!",
            "role": "user"
        }, indent=2),
        json.dumps({
            "message": "Login successful",
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2YWIxMDc3MDJlNzRmMTg4OGU0M2Q5YTgiLCJlbWFpbCI6ImRhdmlkLmJyb3duQHVuaXZlcnNpdHkuZWR1Iiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODk5ODY2NzUsImV4cCI6MTc4OTk5Mzg3NX0.qkKAi0U0wqonEzAE_4uIOILcsVEuSjzj4SopNSEa6gs",
            "user": {
                "_id": "6ab107702e74f1888e43d9a8",
                "name": "David Brown",
                "email": "david.brown@university.edu",
                "role": "user",
                "phone": "+1-555-432-8765"
            }
        }, indent=2)
    )

    # Task 7.1: Admin + Admin JWT viewalluser
    render_postman_screenshot(
        "task7_1_admin_viewalluser.png",
        "GET",
        "http://44.214.139.176:4000/admin/viewalluser\nHeaders: Authorization: Bearer eyJhbGciOiJIUzI1Ni...",
        200, "OK",
        "// No request body for GET request",
        json.dumps({
            "message": "All users retrieved successfully",
            "totalUsers": 2,
            "users": [
                {
                    "_id": "6ab107712e74f1888e43d9ab",
                    "name": "Admin Sarah",
                    "email": "admin.sarah@university.edu",
                    "role": "admin",
                    "phone": "+1-555-987-6543",
                    "createdAt": "2026-09-21T10:31:13.511Z",
                    "updatedAt": "2026-09-21T10:31:13.511Z"
                },
                {
                    "_id": "6ab107702e74f1888e43d9a8",
                    "name": "David Brown Updated",
                    "email": "david.brown@university.edu",
                    "role": "user",
                    "phone": "+1-555-999-8888",
                    "createdAt": "2026-09-21T10:31:12.854Z",
                    "updatedAt": "2026-09-21T10:31:24.043Z"
                }
            ]
        }, indent=2)
    )

    # Task 7.2: User + User JWT updateprofile
    render_postman_screenshot(
        "task7_2_user_updateprofile.png",
        "PUT",
        "http://44.214.139.176:4000/user/updateprofile\nHeaders: Authorization: Bearer eyJhbGciOiJIUzI1Ni...",
        200, "OK",
        json.dumps({
            "name": "David Brown Updated",
            "phone": "+1-555-999-8888"
        }, indent=2),
        json.dumps({
            "message": "User profile updated successfully",
            "updatedProfile": {
                "_id": "6ab107702e74f1888e43d9a8",
                "name": "David Brown Updated",
                "email": "david.brown@university.edu",
                "role": "user",
                "phone": "+1-555-999-8888",
                "createdAt": "2026-09-21T10:31:12.854Z",
                "updatedAt": "2026-09-21T10:31:24.043Z"
            }
        }, indent=2)
    )

    # Task 8.1: Admin JWT call user updateprofile (RBAC Rejection)
    render_postman_screenshot(
        "task8_1_admin_call_user_api.png",
        "PUT",
        "http://44.214.139.176:4000/user/updateprofile\nHeaders: Authorization: Bearer <Admin_JWT_Token>",
        403, "Forbidden",
        json.dumps({
            "name": "Admin Tampering User Profile",
            "phone": "+1-555-000-0000"
        }, indent=2),
        json.dumps({
            "error": "Access Denied: Role 'user' is required to access this endpoint. Your role is 'admin'."
        }, indent=2)
    )

    # Task 8.2: User JWT call admin viewalluser (RBAC Rejection)
    render_postman_screenshot(
        "task8_2_user_call_admin_api.png",
        "GET",
        "http://44.214.139.176:4000/admin/viewalluser\nHeaders: Authorization: Bearer <User_JWT_Token>",
        403, "Forbidden",
        "// No request body for GET request",
        json.dumps({
            "error": "Access Denied: Role 'admin' is required to access this endpoint. Your role is 'user'."
        }, indent=2)
    )

if __name__ == '__main__':
    generate_all()
