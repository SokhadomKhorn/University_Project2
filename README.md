# University Central Identity & User Management Platform
## 5 Independent Microservices Architecture with API Gateway & Role-Based JWT Authentication

This project implements a secure, distributed Central Identity and User Management Platform for university students/staff and administrative staff using **Node.js**, **Express**, **MongoDB / Mongoose**, and **JWT Authentication with Role-Based Access Control (RBAC)**.

---

## 🏛️ System Architecture

```
                      Client (Postman / Web App)
                                  │
                                  ▼
      ┌───────────────────────────────────────────────────────┐
      │               API Gateway Microservice                │
      │                  (Port: 4000)                         │
      │   - Single Entry Point for all Clients                │
      │   - JWT Validation (Signature & Expiration)           │
      │   - Role-Based Routing (Admin vs User Enforcement)    │
      └───────┬──────────────┬──────────────┬─────────────────┘
              │              │              │                 │
              ▼              ▼              ▼                 ▼
      ┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
      │ Registration ││    Login     ││    Admin     ││     User     │
      │   Service    ││   Service    ││   Service    ││   Service    │
      │ (Port: 5001) ││ (Port: 5002) ││ (Port: 5003) ││ (Port: 5004) │
      └───────┬──────┘└──────┬───────┘└──────┬───────┘└──────┬───────┘
              │              │              │                 │
              ▼              ▼              ▼                 ▼
      ┌──────────────────────────────────────────────────────────────┐
      │                       MongoDB Database                       │
      │                   `university_identity_db`                   │
      └──────────────────────────────────────────────────────────────┘
```

---

## 📦 Microservices Breakdown

| Service | Port | Endpoint(s) | Access Type | Description |
|---|---|---|---|---|
| **API Gateway** | `4000` | `/*` | Public / Gatekeeper | Single-entry gateway; routes requests to downstream services and verifies JWT tokens & roles. |
| **Registration Microservice** | `5001` | `POST /register/userregister` | Public (via Gateway) | Validates unique email, hashes password with `bcryptjs`, and creates user in MongoDB. |
| **Login Microservice** | `5002` | `POST /auth/login` | Public (via Gateway) | Authenticates email, password, and role; returns signed JWT token. |
| **Admin Microservice** | `5003` | `GET /admin/searchuser`<br>`GET /admin/viewalluser`<br>`DELETE /admin/deluser` | Protected (**Admin Only**) | Administrative tasks: search user by name/email, view all user records, delete a user by email. |
| **User Microservice** | `5004` | `GET /user/viewprofile`<br>`PUT /user/updateprofile` | Protected (**User Only**) | Profile management for students/staff: view and update own profile. |

---

## 🔐 Security & Role-Based Access Control (RBAC)

1. **Password Security**: Passwords are never stored as plain text. They are securely salted and hashed using `bcryptjs` (salt rounds: 10).
2. **JWT Authentication**: Login returns a JWT signed with payload `{ userId, email, role }` and 2-hour expiration.
3. **Gateway Protection**:
   - Rejects requests with **no token** with `401 Unauthorized`.
   - Rejects requests with **expired or tampered tokens** with `401 / 403 Forbidden`.
   - Rejects ordinary **Users** attempting to access Admin APIs (`/admin/*`) with `403 Forbidden`.
   - Rejects **Admins** attempting to access User-only APIs (`/user/*`) with `403 Forbidden`.

---

## 🗄️ Database Model (Task 3)

The MongoDB User Model contains the following fields:
```json
{
  "_id": "65eaf1444fb4eaf480000000000",
  "name": "Alice Johnson",
  "email": "alice@university.edu",
  "password": "$2a$10$e5j0N3v8b2K...",
  "role": "user",
  "phone": "+1-555-0199",
  "createdAt": "2026-09-10T08:50:00.000Z",
  "updatedAt": "2026-09-10T08:50:00.000Z"
}
```

---

## 🚀 How to Run Locally

### 1. Install Dependencies
```bash
cd Identity_Platform
npm install
```

### 2. Start All 5 Microservices Concurrently
```bash
node start-all.js
```
*Alternatively, you can run:*
```bash
npm run start:all
```

### 3. Run Automated End-to-End Test Suite (Tasks 4 - 10)
In a separate terminal window:
```bash
node test-suite.js
```

---

## 🧪 Postman Testing Guide

Import the included `Identity_Platform_Postman_Collection.json` into Postman. It includes pre-configured requests organized by task:

1. **Task 5 (Registration)**:
   - `POST http://localhost:4000/register/userregister` (User & Admin Registration + Duplicate Email rejection test).
2. **Task 6 (Login)**:
   - `POST http://localhost:4000/auth/login` (User login, Admin login, Invalid password test, Invalid role test).
3. **Task 8 (Admin Microservice)**:
   - `GET http://localhost:4000/admin/searchuser?query=alice` (Found).
   - `GET http://localhost:4000/admin/searchuser?query=nonexistent` (Not Found 404).
   - `GET http://localhost:4000/admin/viewalluser` (View all users).
   - `DELETE http://localhost:4000/admin/deluser?email=delete.me@university.edu` (Delete user).
4. **Task 9 (User Microservice)**:
   - `GET http://localhost:4000/user/viewprofile` (View own profile).
   - `PUT http://localhost:4000/user/updateprofile` (Update own profile).
5. **Task 10 (Security & RBAC Enforcement)**:
   - **a)** Access without token (401 Unauthorized).
   - **b)** Access with invalid token (403 Forbidden).
   - **c)** Using Admin token to access User API (403 Forbidden).
   - **d)** Using User token to access Admin API (403 Forbidden).

---

## 📤 GitHub Upload & Submission (Task 11)

To push this repository to GitHub:
```bash
git init
git add .
git commit -m "Complete 5 Microservices Central Identity and User Management Platform"
git branch -M main
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>.git
git push -u origin main
```
