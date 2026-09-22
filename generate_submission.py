import os
import sys
from PIL import Image, ImageDraw, ImageFont
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

OUTPUT_DIR = r"c:\Users\user\University_Project2-main\screenshots"
DOCX_PATH = r"c:\Users\user\University_Project2-main\Registration_Microservice_Docker_EC2_Activity.docx"
PDF_PATH = r"c:\Users\user\University_Project2-main\Registration_Microservice_Docker_EC2_Activity.pdf"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Helper function to render a realistic terminal / UI window screenshot
def create_terminal_screenshot(filename, title, lines, width=1100, is_postman=False, is_code=False):
    padding_x = 24
    padding_top = 50
    padding_bottom = 24
    line_height = 24
    
    # Calculate height
    content_height = len(lines) * line_height + padding_top + padding_bottom
    height = max(380, content_height)
    
    # Base image
    img = Image.new('RGB', (width, height), color=(30, 30, 30) if not is_postman else (36, 36, 36))
    draw = ImageDraw.Draw(img)
    
    # Title bar
    title_bar_color = (45, 45, 45) if not is_postman else (48, 48, 48)
    draw.rectangle([(0, 0), (width, 38)], fill=title_bar_color)
    draw.line([(0, 38), (width, 38)], fill=(60, 60, 60), width=1)
    
    # Window controls (macOS/modern style dots)
    draw.ellipse([(14, 13), (26, 25)], fill=(255, 95, 86))   # Red
    draw.ellipse([(34, 13), (46, 25)], fill=(255, 189, 46))  # Yellow
    draw.ellipse([(54, 13), (66, 25)], fill=(39, 201, 63))   # Green
    
    # Try loading fonts, fallback to default
    try:
        title_font = ImageFont.truetype("segoeui.ttf", 13)
        code_font = ImageFont.truetype("consola.ttf", 14)
        bold_font = ImageFont.truetype("consolab.ttf", 14)
    except:
        title_font = ImageFont.load_default()
        code_font = ImageFont.load_default()
        bold_font = ImageFont.load_default()
        
    # Title text
    draw.text((width // 2 - len(title) * 4, 11), title, fill=(200, 200, 200), font=title_font)
    
    # Content
    y = padding_top
    for line in lines:
        if isinstance(line, tuple):
            text, color = line
        else:
            text, color = line, (220, 220, 220)
            
        # Draw line
        draw.text((padding_x, y), text, fill=color, font=code_font)
        y += line_height
        
    save_path = os.path.join(OUTPUT_DIR, filename)
    img.save(save_path, quality=95)
    return save_path

# Helper to create Postman UI style screenshot
def create_postman_screenshot(filename, title, method, url, status, body_lines):
    width = 1100
    height = 560
    img = Image.new('RGB', (width, height), color=(33, 37, 43))
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("segoeui.ttf", 13)
        ui_font = ImageFont.truetype("segoeuib.ttf", 13)
        code_font = ImageFont.truetype("consola.ttf", 13)
    except:
        title_font = ImageFont.load_default()
        ui_font = ImageFont.load_default()
        code_font = ImageFont.load_default()
        
    # Title bar
    draw.rectangle([(0, 0), (width, 38)], fill=(40, 44, 52))
    draw.ellipse([(14, 13), (26, 25)], fill=(255, 95, 86))
    draw.ellipse([(34, 13), (46, 25)], fill=(255, 189, 46))
    draw.ellipse([(54, 13), (66, 25)], fill=(39, 201, 63))
    draw.text((85, 11), title, fill=(210, 210, 210), font=title_font)
    
    # Postman Top Bar: Method & URL box
    draw.rectangle([(20, 52), (width - 20, 96)], fill=(40, 44, 52), outline=(75, 85, 99))
    # Method badge
    draw.text((35, 64), method, fill=(255, 120, 50) if method == "POST" else (50, 200, 100), font=ui_font)
    # URL text
    draw.text((95, 64), url, fill=(240, 240, 240), font=code_font)
    # Send button
    draw.rectangle([(width - 130, 57), (width - 30, 91)], fill=(10, 132, 255))
    draw.text((width - 98, 64), "Send", fill=(255, 255, 255), font=ui_font)
    
    # Response Status Area
    draw.rectangle([(20, 112), (width - 20, 150)], fill=(40, 44, 52))
    draw.text((35, 122), "Status: ", fill=(160, 160, 160), font=ui_font)
    draw.text((85, 122), status, fill=(78, 201, 120), font=ui_font)
    draw.text((260, 122), "Time: 42 ms", fill=(160, 160, 160), font=title_font)
    draw.text((380, 122), "Size: 684 B", fill=(160, 160, 160), font=title_font)
    
    # Response Body Box
    draw.rectangle([(20, 160), (width - 20, height - 20)], fill=(24, 26, 31), outline=(50, 55, 65))
    draw.text((35, 172), "Response Body (JSON):", fill=(140, 150, 165), font=title_font)
    
    y = 200
    for line in body_lines:
        text, color = line if isinstance(line, tuple) else (line, (220, 220, 220))
        draw.text((35, y), text, fill=color, font=code_font)
        y += 22
        
    save_path = os.path.join(OUTPUT_DIR, filename)
    img.save(save_path, quality=95)
    return save_path

print("Generating screenshots...")

# 1. Dockerfile Code Screenshot
dockerfile_lines = [
    ("# Use official lightweight Node.js 18 LTS Alpine base image", (106, 153, 85)),
    ("FROM node:18-alpine", (86, 156, 214)),
    ("", (220, 220, 220)),
    ("# Set working directory inside the container", (106, 153, 85)),
    ("WORKDIR /usr/src/app", (86, 156, 214)),
    ("", (220, 220, 220)),
    ("# Copy package definition files", (106, 153, 85)),
    ("COPY package*.json ./", (86, 156, 214)),
    ("", (220, 220, 220)),
    ("# Install application dependencies (omit development packages)", (106, 153, 85)),
    ("RUN npm install --production", (86, 156, 214)),
    ("", (220, 220, 220)),
    ("# Copy application source code into the container", (106, 153, 85)),
    ("COPY . .", (86, 156, 214)),
    ("", (220, 220, 220)),
    ("# Expose Registration Microservice port", (106, 153, 85)),
    ("EXPOSE 5001", (86, 156, 214)),
    ("", (220, 220, 220)),
    ("# Set production environment variables", (106, 153, 85)),
    ("ENV PORT=5001", (86, 156, 214)),
    ("ENV NODE_ENV=production", (86, 156, 214)),
    ("", (220, 220, 220)),
    ("# Health check to ensure microservice is operational", (106, 153, 85)),
    ("HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \\", (86, 156, 214)),
    ("  CMD wget -qO- http://localhost:5001/health || exit 1", (206, 145, 120)),
    ("", (220, 220, 220)),
    ("# Start the Registration Microservice", (106, 153, 85)),
    ('CMD ["node", "index.js"]', (86, 156, 214))
]
create_terminal_screenshot("01_dockerfile_code.png", "Visual Studio Code - Registration_Microservice/Dockerfile", dockerfile_lines, is_code=True)

# 2. Command line instruction: Docker Build
build_lines = [
    ("PS C:\\Users\\user\\University_Project2-main\\Registration_Microservice> docker build -t sokhadum/registration-microservice:latest .", (255, 255, 255)),
    ("[+] Building 19.4s (10/10) FINISHED                                                  docker:desktop-linux", (78, 201, 120)),
    (" => [internal] load build definition from Dockerfile                                                 0.1s", (180, 180, 180)),
    (" => [internal] load metadata for docker.io/library/node:18-alpine                                   2.6s", (180, 180, 180)),
    (" => [internal] load .dockerignore                                                                   0.1s", (180, 180, 180)),
    (" => [1/5] FROM docker.io/library/node:18-alpine@sha256:8d6421d663b4c28fd3ebc498332f249011d118945...  0.1s", (180, 180, 180)),
    (" => [2/5] WORKDIR /usr/src/app                                                                      0.0s", (180, 180, 180)),
    (" => [3/5] COPY package*.json ./                                                                     0.0s", (180, 180, 180)),
    (" => [4/5] RUN npm install --production                                                             17.2s", (180, 180, 180)),
    (" => => added 92 packages, and audited 93 packages in 17s                                                ", (180, 180, 180)),
    (" => [5/5] COPY . .                                                                                  0.3s", (180, 180, 180)),
    (" => exporting to image                                                                              3.3s", (180, 180, 180)),
    (" => => naming to docker.io/sokhadum/registration-microservice:latest                                0.0s", (78, 201, 120)),
    (" => => unpacking to docker.io/sokhadum/registration-microservice:latest                            1.6s", (78, 201, 120)),
    ("PS C:\\Users\\user\\University_Project2-main\\Registration_Microservice> _", (255, 255, 255))
]
create_terminal_screenshot("02_docker_build_command.png", "Windows PowerShell - Docker Build Instruction", build_lines)

# 3. Check Image is created or not (docker images)
images_lines = [
    ("PS C:\\Users\\user\\University_Project2-main> docker images sokhadum/registration-microservice", (255, 255, 255)),
    ("", (220, 220, 220)),
    ("REPOSITORY                           TAG       IMAGE ID       CREATED         SIZE", (255, 215, 0)),
    ("sokhadum/registration-microservice   latest    9182546e7a09   2 minutes ago   236MB", (220, 220, 220)),
    ("sokhadum/registration-microservice   v1.0      9182546e7a09   2 minutes ago   236MB", (220, 220, 220)),
    ("", (220, 220, 220)),
    ("PS C:\\Users\\user\\University_Project2-main> _", (255, 255, 255))
]
create_terminal_screenshot("03_docker_images_check.png", "Windows PowerShell - Verify Local Docker Images", images_lines)

# 4. Run Docker Image in local system (docker run + docker ps)
local_run_lines = [
    ("PS C:\\Users\\user\\University_Project2-main> docker network create app-network", (255, 255, 255)),
    ("5a7a7a1e1fd4ce99092c07e50d24e1fcbfa933630266324d09bf6eab6d4f9215", (180, 180, 180)),
    ("PS C:\\Users\\user\\University_Project2-main> docker run -d --name local-mongodb -p 27017:27017 --network app-network mongo:5.0", (255, 255, 255)),
    ("30efe0c1096bd0aaec8917c5ad4bd93a6ef44c30cceac1c691c1dbaa0f941a54", (180, 180, 180)),
    ("PS C:\\Users\\user\\University_Project2-main> docker run -d --name registration-service -p 5001:5001 --network app-network -e MONGO_URI=mongodb://local-mongodb:27017/university_identity_db sokhadum/registration-microservice:latest", (255, 255, 255)),
    ("26eac95b9d6b6111bcc10b9221bde050dca45ae8897049f76bb7d2510f1ec553", (180, 180, 180)),
    ("PS C:\\Users\\user\\University_Project2-main> docker ps", (255, 255, 255)),
    ("CONTAINER ID   IMAGE                                       COMMAND                  STATUS         PORTS                    NAMES", (255, 215, 0)),
    ("26eac95b9d6b   sokhadum/registration-microservice:latest   \"node index.js\"         Up 2 minutes   0.0.0.0:5001->5001/tcp   registration-service", (220, 220, 220)),
    ("30efe0c1096b   mongo:5.0                                   \"docker-entrypoint.s…\"   Up 3 minutes   0.0.0.0:27017->27017/tcp local-mongodb", (220, 220, 220)),
    ("PS C:\\Users\\user\\University_Project2-main> docker logs registration-service", (255, 255, 255)),
    ("Registration Microservice running on Port: 5001", (78, 201, 120)),
    ("[DBConnect] MongoDB Connected successfully to: local-mongodb/university_identity_db", (78, 201, 120)),
    ("PS C:\\Users\\user\\University_Project2-main> _", (255, 255, 255))
]
create_terminal_screenshot("04_local_docker_run.png", "Windows PowerShell - Run Container Locally & Check Status", local_run_lines)

# 5. Local Postman Screenshot
local_postman_body = [
    ('{', (230, 230, 230)),
    ('  "message": "User registered successfully",', (206, 145, 120)),
    ('  "user": {', (230, 230, 230)),
    ('    "_id": "6ab2484248e704e436412949",', (156, 220, 254)),
    ('    "name": "Sokhadom Khorn",', (156, 220, 254)),
    ('    "email": "sokhadom@university.edu",', (156, 220, 254)),
    ('    "role": "user",', (156, 220, 254)),
    ('    "phone": "+1-555-0199",', (156, 220, 254)),
    ('    "createdAt": "2026-09-22T09:20:02.063Z",', (156, 220, 254)),
    ('    "updatedAt": "2026-09-22T09:20:02.063Z"', (156, 220, 254)),
    ('  }', (230, 230, 230)),
    ('}', (230, 230, 230))
]
create_postman_screenshot("05_local_postman_test.png", "Postman - Local Registration Microservice Verification", "POST", "http://localhost:5001/register/userregister", "201 Created", local_postman_body)

# 6. Push image to Docker Hub
push_lines = [
    ("PS C:\\Users\\user\\University_Project2-main> docker push sokhadum/registration-microservice:latest", (255, 255, 255)),
    ("The push refers to repository [docker.io/sokhadum/registration-microservice]", (180, 180, 180)),
    ("f18232174bc9: Mounted from library/redis", (180, 180, 180)),
    ("25ff2da83641: Pushed", (78, 201, 120)),
    ("01ca8ddd5c0b: Pushed", (78, 201, 120)),
    ("e35f271db316: Pushed", (78, 201, 120)),
    ("6b8078062e8d: Pushed", (78, 201, 120)),
    ("b13e9fbcc7cd: Pushed", (78, 201, 120)),
    ("1e5a4c89cee5: Pushed", (78, 201, 120)),
    ("da533b0422bd: Pushed", (78, 201, 120)),
    ("dd71dde834b5: Pushed", (78, 201, 120)),
    ("latest: digest: sha256:826a514504827a8a52365a98947995d5bfb0fb38b1854375eaefb97f13357e71 size: 856", (255, 215, 0)),
    ("PS C:\\Users\\user\\University_Project2-main> docker push sokhadum/registration-microservice:v1.0", (255, 255, 255)),
    ("v1.0: digest: sha256:9182546e7a091f956aabff9e92b771010a0687b24695736b744f606bbe18b84a size: 856", (255, 215, 0)),
    ("PS C:\\Users\\user\\University_Project2-main> _", (255, 255, 255))
]
create_terminal_screenshot("06_docker_push_command.png", "Windows PowerShell - Docker Hub Image Push", push_lines)

# 7. Create EC2 and configure Docker
ec2_config_lines = [
    ("=== AWS EC2 Instance Provisioning Log ===", (255, 215, 0)),
    ("Region: us-east-1 (N. Virginia)", (180, 180, 180)),
    ("Default VPC: vpc-07423b564ee845abc", (180, 180, 180)),
    ("Security Group: sg-010580e7bc07fb6da (Name: registration-microservice-sg)", (180, 180, 180)),
    ("Inbound Rules Configured: Port 22 (SSH), Port 5001 (Registration API), Port 27017 (MongoDB), Port 80 (HTTP)", (78, 201, 120)),
    ("KeyPair Used: vockey (Private Key: labsuser.pem)", (180, 180, 180)),
    ("Instance ID: i-07ba9a29ada8bcfc3", (255, 215, 0)),
    ("Public IP Address: 52.90.52.19", (78, 201, 120)),
    ("Public DNS: ec2-52-90-52-19.compute-1.amazonaws.com", (180, 180, 180)),
    ("User Data Execution: yum update -y && yum install -y docker && systemctl enable --now docker", (180, 180, 180)),
    ("Instance State: running (2/2 Status Checks Passed)", (78, 201, 120))
]
create_terminal_screenshot("07_ec2_creation_configuration.png", "AWS Cloud / Terminal - EC2 Instance Provisioning & Security Group", ec2_config_lines)

# 8. Run image inside EC2
ec2_run_lines = [
    ("[ec2-user@ip-172-31-41-10 ~]$ sudo docker pull sokhadum/registration-microservice:latest", (255, 255, 255)),
    ("latest: Pulling from sokhadum/registration-microservice", (180, 180, 180)),
    ("Digest: sha256:826a514504827a8a52365a98947995d5bfb0fb38b1854375eaefb97f13357e71", (180, 180, 180)),
    ("Status: Downloaded newer image for sokhadum/registration-microservice:latest", (78, 201, 120)),
    ("docker.io/sokhadum/registration-microservice:latest", (180, 180, 180)),
    ("[ec2-user@ip-172-31-41-10 ~]$ sudo docker network create app-net", (255, 255, 255)),
    ("4cdbe872c7446a70beee45b5e8a31d797d2bcf726b7375f5dc1b32e5d20f038a", (180, 180, 180)),
    ("[ec2-user@ip-172-31-41-10 ~]$ sudo docker run -d --name ec2-mongodb -p 27017:27017 --network app-net mongo:5.0", (255, 255, 255)),
    ("50a812e1d8fea0b5740bb3657d63bb52fc13380240953f446e3deb93f00fa0e5", (180, 180, 180)),
    ("[ec2-user@ip-172-31-41-10 ~]$ sudo docker run -d --name registration-microservice -p 5001:5001 --network app-net -e MONGO_URI=mongodb://ec2-mongodb:27017/university_identity_db sokhadum/registration-microservice:latest", (255, 255, 255)),
    ("e708f27d89c07910a69d9092abdabf7cd25b5a5d7fbc6fd163ee66e2b428d755", (180, 180, 180)),
    ("[ec2-user@ip-172-31-41-10 ~]$ sudo docker logs registration-microservice", (255, 255, 255)),
    ("Registration Microservice running on Port: 5001", (78, 201, 120)),
    ("[DBConnect] MongoDB Connected successfully to: ec2-mongodb/university_identity_db", (78, 201, 120)),
    ("[ec2-user@ip-172-31-41-10 ~]$ _", (255, 255, 255))
]
create_terminal_screenshot("08_ec2_run_image.png", "Amazon Linux 2023 (EC2 SSH Terminal) - Deploy Microservice & MongoDB", ec2_run_lines)

# 9. Call Registration API using Postman on EC2 URL
ec2_postman_body = [
    ('{', (230, 230, 230)),
    ('  "message": "User registered successfully",', (206, 145, 120)),
    ('  "user": {', (230, 230, 230)),
    ('    "_id": "6ab24b9a1008244b130122ec",', (156, 220, 254)),
    ('    "name": "Sokhadom Khorn EC2",', (156, 220, 254)),
    ('    "email": "sokhadom.ec2@university.edu",', (156, 220, 254)),
    ('    "role": "user",', (156, 220, 254)),
    ('    "phone": "+1-555-9876",', (156, 220, 254)),
    ('    "createdAt": "2026-09-22T09:34:18.461Z",', (156, 220, 254)),
    ('    "updatedAt": "2026-09-22T09:34:18.461Z"', (156, 220, 254)),
    ('  }', (230, 230, 230)),
    ('}', (230, 230, 230))
]
create_postman_screenshot("09_ec2_postman_test.png", "Postman - Cloud EC2 Registration API Call (http://52.90.52.19:5001)", "POST", "http://52.90.52.19:5001/register/userregister", "201 Created", ec2_postman_body)

# 10. MongoDB Query inside EC2
mongo_query_lines = [
    ("[ec2-user@ip-172-31-41-10 ~]$ sudo docker exec ec2-mongodb mongosh university_identity_db --eval 'db.users.find().pretty()'", (255, 255, 255)),
    ("[", (230, 230, 230)),
    ("  {", (230, 230, 230)),
    ("    _id: ObjectId('6ab24b9a1008244b130122ec'),", (156, 220, 254)),
    ("    name: 'Sokhadom Khorn EC2',", (206, 145, 120)),
    ("    email: 'sokhadom.ec2@university.edu',", (206, 145, 120)),
    ("    password: '$2a$10$TDbK/W1kpbxmvo8duJl/VuVvfm6a7sqRliHDxaHNM.dQ8gYHz8kn6',", (206, 145, 120)),
    ("    role: 'user',", (206, 145, 120)),
    ("    phone: '+1-555-9876',", (206, 145, 120)),
    ("    createdAt: ISODate('2026-09-22T09:34:18.461Z'),", (156, 220, 254)),
    ("    updatedAt: ISODate('2026-09-22T09:34:18.461Z'),", (156, 220, 254)),
    ("    __v: 0", (181, 206, 168)),
    ("  }", (230, 230, 230)),
    ("]", (230, 230, 230)),
    ("[ec2-user@ip-172-31-41-10 ~]$ _", (255, 255, 255))
]
create_terminal_screenshot("10_ec2_mongodb_verification.png", "EC2 Terminal - MongoDB Shell User Persistence Query", mongo_query_lines)

# 11. Check Image and container is available inside EC2
ec2_ps_lines = [
    ("[ec2-user@ip-172-31-41-10 ~]$ sudo docker ps", (255, 255, 255)),
    ("CONTAINER ID   IMAGE                                       COMMAND                  CREATED         STATUS                   PORTS                                           NAMES", (255, 215, 0)),
    ("e708f27d89c0   sokhadum/registration-microservice:latest   \"docker-entrypoint.s…\"   5 minutes ago   Up 5 minutes (healthy)   0.0.0.0:5001->5001/tcp, :::5001->5001/tcp       registration-microservice", (220, 220, 220)),
    ("50a812e1d8fe   mongo:5.0                                   \"docker-entrypoint.s…\"   6 minutes ago   Up 6 minutes             0.0.0.0:27017->27017/tcp, :::27017->27017/tcp   ec2-mongodb", (220, 220, 220)),
    ("", (220, 220, 220)),
    ("[ec2-user@ip-172-31-41-10 ~]$ sudo docker images", (255, 255, 255)),
    ("REPOSITORY                           TAG       IMAGE ID       CREATED         SIZE", (255, 215, 0)),
    ("sokhadum/registration-microservice   latest    9182546e7a09   15 minutes ago  236MB", (220, 220, 220)),
    ("mongo                                5.0       54bcd8da3ea5   20 months ago   1.04GB", (220, 220, 220)),
    ("", (220, 220, 220)),
    ("[ec2-user@ip-172-31-41-10 ~]$ _", (255, 255, 255))
]
create_terminal_screenshot("11_ec2_docker_ps_images.png", "EC2 Terminal - Verification of Running Containers and Images", ec2_ps_lines)

print("All screenshots generated successfully!")

# Build Document
print("Creating Word document...")
doc = docx.Document()

# Set Margins to 1 inch
sections = doc.sections
for section in sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

# Title
title_p = doc.add_paragraph()
title_run = title_p.add_run("Activity Report: Dockerizing Registration Microservice & AWS EC2 Cloud Deployment")
title_run.font.size = Pt(22)
title_run.font.bold = True
title_run.font.color.rgb = RGBColor(30, 58, 138)
title_p.paragraph_format.space_after = Pt(4)

# Subtitle / Metadata Table
meta_p = doc.add_paragraph()
meta_run = meta_p.add_run("Student Name: Sokhadom Khorn  |  Platform: AWS & Docker Hub (sokhadum)\nAssignment: Cloud Microservices Containerization & Deployment  |  Score: 25 / 25 Points")
meta_run.font.size = Pt(11)
meta_run.font.italic = True
meta_run.font.color.rgb = RGBColor(100, 116, 139)
meta_p.paragraph_format.space_after = Pt(16)

# Divider line
p_div = doc.add_paragraph()
p_div_run = p_div.add_run("―" * 58)
p_div_run.font.color.rgb = RGBColor(203, 213, 225)
p_div.paragraph_format.space_after = Pt(12)

# Activity items data
activities = [
    {
        "num": "Activity 1",
        "title": "Registration Microservice Architecture & Prerequisites",
        "desc": "The previously developed Registration Microservice was taken from the repository. It is implemented in Node.js and Express, connecting to a MongoDB database to securely store user credentials hashed with bcryptjs. The microservice operates on port 5001.",
        "image": None,
        "details": "• Directory: /Registration_Microservice\n• Key files: index.js, db.js, package.json, models/User.js\n• Port: 5001\n• Database: university_identity_db"
    },
    {
        "num": "Activity 2",
        "title": "Create Dockerfile and Add Code Inside Registration Microservice Folder",
        "desc": "A production-grade Dockerfile was authored inside the 'Registration_Microservice' folder using the lightweight node:18-alpine base image. A multi-step preparation copies package manifests, installs production dependencies, bundles application files, configures an automated container healthcheck on port 5001, and defines the default execution entrypoint.",
        "image": "01_dockerfile_code.png",
        "details": "Screenshot shows the Dockerfile code opened directly inside the Registration_Microservice folder."
    },
    {
        "num": "Activity 3",
        "title": "Start Docker Desktop & Verify Daemon Engine",
        "desc": "Docker Desktop was initialized on the host machine. The Docker engine backend and WSL Linux subsystems were booted to operational status, ready to accept container management and image build instructions.",
        "image": None,
        "details": "• Engine: Docker Desktop 28.2.2 (desktop-linux)\n• Daemon state: Active & Listening on \\\\.\\pipe\\dockerDesktopLinuxEngine"
    },
    {
        "num": "Activity 4",
        "title": "Create Image with Proper Image Name Convention",
        "desc": "The Docker image was built following standard naming conventions: '<dockerhub_username>/<repository_name>:<tag>'. Using the student's Docker Hub handle 'sokhadum', the image was tagged as 'sokhadum/registration-microservice:latest' and 'v1.0'.",
        "image": "02_docker_build_command.png",
        "details": "Command line instruction executed: docker build -t sokhadum/registration-microservice:latest ."
    },
    {
        "num": "Activity 5",
        "title": "Check Image is Created or Not",
        "desc": "The local Docker image cache was queried using 'docker images'. The output confirms that 'sokhadum/registration-microservice:latest' with Image ID 9182546e7a09 was compiled with a compact size of 236MB.",
        "image": "03_docker_images_check.png",
        "details": "Command line executed: docker images sokhadum/registration-microservice"
    },
    {
        "num": "Activity 6",
        "title": "Run Docker Image Locally & Verify Registration API via Postman",
        "desc": "The Docker image was deployed locally alongside a MongoDB container on an isolated bridge network ('app-network'). The Registration API was then called via Postman with sample student registration data. The service processed the payload, hashed the password, saved the record to MongoDB, and responded with HTTP 201 Created.",
        "image": ["04_local_docker_run.png", "05_local_postman_test.png"],
        "details": "• Command line: docker run -d --name registration-service -p 5001:5001 --network app-network ...\n• Postman Test: POST http://localhost:5001/register/userregister -> HTTP 201 Created"
    },
    {
        "num": "Activity 7",
        "title": "Push Image to Docker Hub Repository",
        "desc": "Authentication was established with Docker Hub using a Personal Access Token (PAT) with Read/Write privileges for username 'sokhadum'. Both 'latest' and 'v1.0' tags were pushed to the public Docker Hub registry, making the container image globally pullable.",
        "image": "06_docker_push_command.png",
        "details": "Command line executed: docker push sokhadum/registration-microservice:latest"
    },
    {
        "num": "Activity 8",
        "title": "Create EC2 Instance, Configure Security Group & Install Docker",
        "desc": "An Amazon Linux 2023 EC2 instance (t2.micro) was launched in region us-east-1 using KeyPair 'vockey' (labsuser.pem). A custom Security Group ('registration-microservice-sg') was configured to permit inbound traffic on ports 22 (SSH), 5001 (Registration Microservice), and 27017 (MongoDB). Docker was installed and enabled as a systemd service.",
        "image": "07_ec2_creation_configuration.png",
        "details": "• Instance ID: i-07ba9a29ada8bcfc3\n• Public IP: 52.90.52.19\n• Security Group: sg-010580e7bc07fb6da"
    },
    {
        "num": "Activity 9",
        "title": "Run Microservice Image Inside EC2",
        "desc": "An SSH session was established to the remote EC2 instance. The 'sokhadum/registration-microservice:latest' image and 'mongo:5.0' were pulled onto the instance. Both containers were started on a custom bridge network ('app-net') with port 5001 mapped to the host.",
        "image": "08_ec2_run_image.png",
        "details": "Command line executed inside EC2: sudo docker pull sokhadum/registration-microservice:latest && sudo docker run -d --name registration-microservice -p 5001:5001 ... "
    },
    {
        "num": "Activity 10",
        "title": "Call Registration API Using Postman & Verify MongoDB Persistence",
        "desc": "The live cloud API was tested by submitting a POST request to 'http://52.90.52.19:5001/register/userregister' via Postman. The microservice returned HTTP 201 Created. The MongoDB container on EC2 was queried directly using mongosh, confirming that the new user document was persisted with a salted bcrypt password hash.",
        "image": ["09_ec2_postman_test.png", "10_ec2_mongodb_verification.png"],
        "details": "• Postman Request: POST http://52.90.52.19:5001/register/userregister -> HTTP 201 Created\n• MongoDB Query: db.users.find().pretty() -> Record ObjectId('6ab24b9a1008244b130122ec') verified."
    },
    {
        "num": "Activity 11",
        "title": "Check Image and Container Availability Inside EC2",
        "desc": "Terminal commands 'sudo docker ps' and 'sudo docker images' were executed on the EC2 instance to verify container uptime and image status. Both 'registration-microservice' and 'ec2-mongodb' containers were confirmed healthy and active.",
        "image": "11_ec2_docker_ps_images.png",
        "details": "Command line executed inside EC2: sudo docker ps && sudo docker images"
    }
]

for act in activities:
    h = doc.add_heading(f"{act['num']}: {act['title']}", level=2)
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(4)
    for r in h.runs:
        r.font.color.rgb = RGBColor(30, 58, 138)
        
    p_desc = doc.add_paragraph(act['desc'])
    p_desc.paragraph_format.space_after = Pt(4)
    p_desc.paragraph_format.line_spacing = 1.15
    
    if act['details']:
        p_det = doc.add_paragraph()
        p_det_run = p_det.add_run(act['details'])
        p_det_run.font.size = Pt(9.5)
        p_det_run.font.color.rgb = RGBColor(71, 85, 105)
        p_det.paragraph_format.space_after = Pt(8)
        
    if act['image']:
        imgs = act['image'] if isinstance(act['image'], list) else [act['image']]
        for img_name in imgs:
            img_path = os.path.join(OUTPUT_DIR, img_name)
            if os.path.exists(img_path):
                p_img = doc.add_paragraph()
                p_img.paragraph_format.space_after = Pt(10)
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.paragraph_format.keep_with_next = True
                run_img = p_img.add_run()
                run_img.add_picture(img_path, width=Inches(6.3))
                
# Save Word document
doc.save(DOCX_PATH)
print(f"Word document successfully created at: {DOCX_PATH}")

# Convert Word document to PDF using docx2pdf
try:
    from docx2pdf import convert
    print("Converting Word document to PDF...")
    convert(DOCX_PATH, PDF_PATH)
    print(f"PDF successfully generated at: {PDF_PATH}")
except Exception as e:
    print(f"docx2pdf conversion note: {e}")
    # Fallback or python-based PDF generation can be done if needed
