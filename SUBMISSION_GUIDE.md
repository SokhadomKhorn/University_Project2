# Central Identity & User Management Platform
## 5 Microservices Architecture with API Gateway & Role-Based JWT Authentication

---

## 📌 Table of Contents
1. [Architecture Overview & Port Allocation](#1-architecture-overview--port-allocation)
2. [Task 1: Microservices Setup & Installed Libraries](#task-1-microservices-setup--installed-libraries)
3. [Task 2: Database Connection (`db.js`)](#task-2-database-connection-dbjs)
4. [Task 3: MongoDB User Model](#task-3-mongodb-user-model)
5. [Task 4: API Gateway Microservice & Routing](#task-4-api-gateway-microservice--routing)
6. [Task 5: Registration Microservice API](#task-5-registration-microservice-api)
7. [Task 6: Login Microservice API & JWT Generation](#task-6-login-microservice-api--jwt-generation)
8. [Task 7: JWT Authentication & Role-Based Access Control (RBAC)](#task-7-jwt-authentication--role-based-access-control-rbac)
9. [Task 8: Admin Microservice APIs](#task-8-admin-microservice-apis)
10. [Task 9: User Microservice APIs](#task-9-user-microservice-apis)
11. [Task 10: Security & Negative Access Control Testing](#task-10-security--negative-access-control-testing)
12. [Task 11: GitHub Repository & Submission Checklist](#task-11-github-repository--submission-checklist)
13. [Step-by-Step Word Document & Single PDF Conversion Guide](#step-by-step-word-document--single-pdf-conversion-guide)

---

## 1. Architecture Overview & Port Allocation

```
Client (Postman / Browser)
           │
           ▼ (Port 4000)
┌────────────────────────────────────────────────────────┐
│               API Gateway Microservice                 │
│  - Single Entry Point                                  │
│  - JWT Signature & Expiration Validation               │
│  - Role Verification (Admin vs User Enforcement)       │
│  - Request Proxying to Target Services                 │
└──────┬───────────────┬────────────────┬────────────────┘
       │               │                │                │
       ▼               ▼                ▼                ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│ Registration ││    Login     ││    Admin     ││     User     │
│   Service    ││   Service    ││   Service    ││   Service    │
│  (Port 5001) ││  (Port 5002) ││  (Port 5003) ││  (Port 5004) │
└──────┬───────┘└──────┬───────┘└──────┬───────┘└──────┬───────┘
       │               │                │                │
       ▼               ▼                ▼                ▼
┌────────────────────────────────────────────────────────┐
│                   MongoDB Database                     │
│               `university_identity_db`                 │
└────────────────────────────────────────────────────────┘
```

| Microservice | Port | Description | Access Type |
|---|---|---|---|
| **API Gateway** | `4000` | Single entry point, JWT verification & RBAC routing | Public Gatekeeper |
| **Registration Microservice** | `5001` | Handles user/admin account registration & bcrypt hashing | Public (via `/register/*`) |
| **Login Microservice** | `5002` | Authenticates email, password, and role; issues JWT | Public (via `/auth/*`) |
| **Admin Microservice** | `5003` | User search, view all users, delete user | Protected (**Admin Only**) |
| **User Microservice** | `5004` | View own profile, update own profile | Protected (**User Only**) |

---

## Task 1: Microservices Setup & Installed Libraries

### Libraries Used:
- `express`: Core Web Framework
- `mongoose`: MongoDB Object Data Modeling (ODM)
- `jsonwebtoken`: Signing, encoding, and verifying JWT tokens
- `bcryptjs`: Password hashing with salt rounds
- `http-proxy`: Reverse proxy routing at API Gateway
- `cors`: Cross-Origin Resource Sharing middleware
- `concurrently`: Multi-service orchestrator for development

---

## Task 2: Database Connection (`db.js`)
Located in all microservices connecting to MongoDB (`Registration_Microservice`, `Login_Microservice`, `Admin_Microservice`, `User_Microservice`).

```javascript
const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    const mongoURI = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/university_identity_db';
    const conn = await mongoose.connect(mongoURI);
    console.log(`[DBConnect] MongoDB Connected successfully: ${conn.connection.host}/${conn.connection.name}`);
    return conn;
  } catch (error) {
    console.error(`[DBConnect] MongoDB Connection Error: ${error.message}`);
  }
};

module.exports = connectDB;
```

---

## Task 3: MongoDB User Model
Located in `models/User.js`:

```javascript
const mongoose = require('mongoose');

const userSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: [true, 'Name is required'],
      trim: true
    },
    email: {
      type: String,
      required: [true, 'Email is required'],
      unique: true,
      lowercase: true,
      trim: true
    },
    password: {
      type: String,
      required: [true, 'Password is required']
    },
    role: {
      type: String,
      required: [true, 'Role is required'],
      enum: ['admin', 'user'],
      default: 'user'
    },
    phone: {
      type: String,
      required: [true, 'Phone number is required'],
      trim: true
    }
  },
  {
    timestamps: true // Automatically manages createdAt and updatedAt
  }
);

module.exports = mongoose.models.User || mongoose.model('User', userSchema);
```

---

## Task 4 & 7: API Gateway Microservice & Routing
Located in `APIGateway_Microservice/index.js`.
Handles:
- Token extraction (`Authorization: Bearer <token>`)
- Rejection of missing tokens (`401 Unauthorized`)
- Rejection of expired or tampered tokens (`401`/`403`)
- Enforcement of Role:
  - Non-admin accessing `/admin/*` -> `403 Forbidden`
  - Non-user (admin) accessing `/user/*` -> `403 Forbidden`
- Forwards user identity claims in headers (`x-user-id`, `x-user-email`, `x-user-role`).

---

## Task 5: Registration Microservice API
- **Endpoint**: `POST http://localhost:4000/register/userregister`
- **Request Body**:
```json
{
  "name": "Alice Johnson",
  "email": "alice@university.edu",
  "password": "alicePass123!",
  "role": "user",
  "phone": "+1-555-0199"
}
```
- **Success Response (201 Created)**:
```json
{
  "message": "User registered successfully",
  "user": {
    "_id": "65e...",
    "name": "Alice Johnson",
    "email": "alice@university.edu",
    "role": "user",
    "phone": "+1-555-0199",
    "createdAt": "2026-09-10T08:50:00.000Z",
    "updatedAt": "2026-09-10T08:50:00.000Z"
  }
}
```
- **Duplicate Email Response (400 Bad Request)**:
```json
{
  "error": "Duplicate Email: An account with this email address already exists."
}
```

---

## Task 6: Login Microservice API
- **Endpoint**: `POST http://localhost:4000/auth/login`
- **Request Body**:
```json
{
  "email": "alice@university.edu",
  "password": "alicePass123!",
  "role": "user"
}
```
- **Success Response (200 OK)**:
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "_id": "65e...",
    "name": "Alice Johnson",
    "email": "alice@university.edu",
    "role": "user",
    "phone": "+1-555-0199"
  }
}
```
- **Invalid Email, Password or Role Response (401 Unauthorized)**:
```json
{
  "error": "Invalid Email or Password or role"
}
```

---

## Task 8: Admin Microservice APIs
All require `Authorization: Bearer <admin_token>`

1. **Search User (Found)**:
   - `GET http://localhost:4000/admin/searchuser?query=alice`
   - Response (200 OK):
   ```json
   {
     "message": "User found successfully",
     "count": 1,
     "users": [ { "name": "Alice Johnson", "email": "alice@university.edu", "role": "user", "phone": "+1-555-0199" } ]
   }
   ```
2. **Search User (Not Found)**:
   - `GET http://localhost:4000/admin/searchuser?query=unknown999`
   - Response (404 Not Found):
   ```json
   {
     "message": "User Not Found",
     "error": "No user found matching the provided search criteria."
   }
   ```
3. **View All Users**:
   - `GET http://localhost:4000/admin/viewalluser`
   - Response (200 OK):
   ```json
   {
     "message": "All users retrieved successfully",
     "totalUsers": 2,
     "users": [ ... ]
   }
   ```
4. **Delete User**:
   - `DELETE http://localhost:4000/admin/deluser?email=bob.temp@university.edu`
   - Response (200 OK):
   ```json
   {
     "message": "User with email 'bob.temp@university.edu' deleted successfully",
     "deletedUser": { "name": "Bob Temporary", "email": "bob.temp@university.edu", "role": "user" }
   }
   ```

---

## Task 9: User Microservice APIs
All require `Authorization: Bearer <user_token>`

1. **View Own Profile**:
   - `GET http://localhost:4000/user/viewprofile`
   - Response (200 OK):
   ```json
   {
     "message": "User profile retrieved successfully",
     "profile": {
       "_id": "65e...",
       "name": "Alice Johnson",
       "email": "alice@university.edu",
       "role": "user",
       "phone": "+1-555-0199"
     }
   }
   ```
2. **Update Own Profile**:
   - `PUT http://localhost:4000/user/updateprofile`
   - Request Body:
   ```json
   {
     "name": "Alice Johnson Updated",
     "phone": "+1-555-9988"
   }
   ```
   - Response (200 OK):
   ```json
   {
     "message": "User profile updated successfully",
     "updatedProfile": {
       "_id": "65e...",
       "name": "Alice Johnson Updated",
       "email": "alice@university.edu",
       "role": "user",
       "phone": "+1-555-9988"
     }
   }
   ```

---

## Task 10: Security & Negative Access Control Testing

### a) Without Token
- Request: `GET http://localhost:4000/admin/viewalluser` (No Authorization header)
  - **Output (401)**: `{"error": "Access Denied: No token provided. Please include a valid Bearer token in the Authorization header."}`
- Request: `GET http://localhost:4000/user/viewprofile` (No Authorization header)
  - **Output (401)**: `{"error": "Access Denied: No token provided. Please include a valid Bearer token in the Authorization header."}`

### b) With Wrong / Tampered Token
- Request: `GET http://localhost:4000/admin/viewalluser` (Header: `Authorization: Bearer invalid.tampered.token`)
  - **Output (403)**: `{"error": "Access Denied: Invalid or tampered token."}`

### c) Using Admin Token to Access User API
- Request: `GET http://localhost:4000/user/viewprofile` (Header: `Authorization: Bearer <admin_token>`)
  - **Output (403)**: `{"error": "Access Denied: Role 'user' is required to access this endpoint. Your role is 'admin'."}`

### d) Using User Token to Access Admin API
- Request: `GET http://localhost:4000/admin/viewalluser` (Header: `Authorization: Bearer <user_token>`)
  - **Output (403)**: `{"error": "Access Denied: Role 'admin' is required to access this endpoint. Your role is 'user'."}`

---

## Step-by-Step Word Document & Single PDF Conversion Guide

### Structure of Your Submission Document:
1. **Title Page**: Assignment Title, Name, Student ID, Course Name.
2. **Task 1 to Task 3**:
   - Screenshot of Folder Structure (showing 5 microservice folders).
   - Screenshot of `db.js` code.
   - Screenshot of `models/User.js` code.
3. **Task 4 & Task 7**:
   - Screenshot of `APIGateway_Microservice/index.js` showing routing & JWT/RBAC middleware.
4. **Task 5 (Registration Service)**:
   - Postman Screenshot: `POST /register/userregister` (Success 201).
   - Postman Screenshot: Duplicate Email Rejection (Error 400).
   - MongoDB / Compass Screenshot showing the registered user document with hashed password.
5. **Task 6 (Login Service)**:
   - Postman Screenshot: `POST /auth/login` (Success 200 with JWT token).
   - Postman Screenshot: Invalid Password / Invalid Role (Error 401).
6. **Task 8 (Admin Microservice)**:
   - Postman Screenshot: `GET /admin/searchuser` (Found).
   - Postman Screenshot: `GET /admin/searchuser` (Not Found 404).
   - Postman Screenshot: `GET /admin/viewalluser` (View all users).
   - Postman Screenshot: `DELETE /admin/deluser` (Delete user by email).
   - MongoDB Screenshot reflecting user deletion.
7. **Task 9 (User Microservice)**:
   - Postman Screenshot: `GET /user/viewprofile`.
   - Postman Screenshot: `PUT /user/updateprofile`.
   - MongoDB Screenshot reflecting updated profile fields.
8. **Task 10 (Security & RBAC Enforcement)**:
   - Screenshot 10a: Access without token (401).
   - Screenshot 10b: Access with invalid token (403).
   - Screenshot 10c: Admin token accessing User API (403 Forbidden).
   - Screenshot 10d: User token accessing Admin API (403 Forbidden).
9. **Task 11**:
   - Public GitHub Repository URL.

### Converting to Single PDF:
1. In Microsoft Word, click **File** > **Save As** > Choose **PDF (*.pdf)**.
2. Alternatively, save as images and merge on [ilovepdf.com/jpg_to_pdf](https://www.ilovepdf.com/jpg_to_pdf).
3. Submit the single PDF file directly on Canvas.
