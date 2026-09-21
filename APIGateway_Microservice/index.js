const express = require('express');
const httpProxy = require('http-proxy');
const jwt = require('jsonwebtoken');
const cors = require('cors');

const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '..', '.env') });
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 4000;
const JWT_SECRET = process.env.JWT_SECRET || 'UniversitySecretKey2026';

// Microservice Target URLs (Supports direct URLs or EC2 IP variables)
const EC2_2_HOST = process.env.EC2_2_IP || process.env.ADMIN_HOST || 'localhost';
const EC2_3_HOST = process.env.EC2_3_IP || process.env.USER_HOST || 'localhost';

const REGISTRATION_SERVICE = process.env.REGISTRATION_SERVICE || 'http://localhost:5001';
const LOGIN_SERVICE = process.env.LOGIN_SERVICE || 'http://localhost:5002';
const ADMIN_SERVICE = process.env.ADMIN_SERVICE || `http://${EC2_2_HOST}:5003`;
const USER_SERVICE = process.env.USER_SERVICE || `http://${EC2_3_HOST}:5004`;

// Create HTTP Proxy
const proxy = httpProxy.createProxyServer({
  changeOrigin: true
});

// Middleware
app.use(cors());
app.use(express.json());

// Forwarding headers and re-streaming body for http-proxy
proxy.on('proxyReq', (proxyReq, req, res, options) => {
  // Forward user claims if authenticated
  if (req.user) {
    proxyReq.setHeader('x-user-id', req.user.userId || req.user.id || req.user._id || '');
    proxyReq.setHeader('x-user-email', req.user.email || '');
    proxyReq.setHeader('x-user-role', req.user.role || '');
  }

  // If express.json() already parsed the body, write it to proxy stream
  if (req.body && Object.keys(req.body).length > 0) {
    const bodyData = JSON.stringify(req.body);
    proxyReq.setHeader('Content-Type', 'application/json');
    proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
    proxyReq.write(bodyData);
  }
});

// Error handling on proxy server
proxy.on('error', (err, req, res) => {
  console.error('[API Gateway] Proxy Error:', err.message);
  if (!res.headersSent) {
    res.status(502).json({
      error: 'Bad Gateway: Downstream microservice is unavailable.',
      details: err.message
    });
  }
});

// ==========================================
// Task 7: JWT Authentication & Role Middleware
// ==========================================
const verifyTokenAndRole = (requiredRole) => {
  return (req, res, next) => {
    const authHeader = req.headers['authorization'] || req.headers['x-access-token'];

    // 1. Check if token is present
    if (!authHeader) {
      console.warn(`[API Gateway] Unauthorized access attempt to ${req.originalUrl}: No token provided.`);
      return res.status(401).json({
        error: 'Access Denied: No token provided. Please include a valid Bearer token in the Authorization header.'
      });
    }

    // Extract Bearer token
    const token = authHeader.startsWith('Bearer ') ? authHeader.slice(7).trim() : authHeader.trim();

    if (!token) {
      return res.status(401).json({
        error: 'Access Denied: Token format is invalid. Expected format: Bearer <token>'
      });
    }

    // 2. Verify token validity and expiration
    jwt.verify(token, JWT_SECRET, (err, decoded) => {
      if (err) {
        if (err.name === 'TokenExpiredError') {
          console.warn(`[API Gateway] Access attempt with expired token to ${req.originalUrl}`);
          return res.status(401).json({
            error: 'Access Denied: Token expired. Please log in again.'
          });
        }
        console.warn(`[API Gateway] Access attempt with invalid/tampered token to ${req.originalUrl}: ${err.message}`);
        return res.status(403).json({
          error: 'Access Denied: Invalid or tampered token.'
        });
      }

      // 3. Role-Based Access Control (RBAC) Enforcement
      const userRole = (decoded.role || '').toLowerCase();
      const expectedRole = (requiredRole || '').toLowerCase();

      if (expectedRole && userRole !== expectedRole) {
        console.warn(
          `[API Gateway] Forbidden access attempt to ${req.originalUrl}. Role '${userRole}' cannot access '${expectedRole}' endpoint.`
        );
        return res.status(403).json({
          error: `Access Denied: Role '${expectedRole}' is required to access this endpoint. Your role is '${userRole}'.`
        });
      }

      // Attach decoded payload to request
      req.user = decoded;
      next();
    });
  };
};

// ==========================================
// Gateway Routes & Routing Code
// ==========================================

// Health Check
app.get('/', (req, res) => {
  res.json({
    platform: 'Central Identity and User Management Platform',
    status: 'API Gateway Active',
    routes: {
      register: '/register/userregister (Public)',
      login: '/auth/login (Public)',
      admin: '/admin/* (Protected: Admin role required)',
      user: '/user/* (Protected: User role required)'
    }
  });
});

// Task 5: Registration Microservice Routing (Public)
app.use('/register', (req, res) => {
  console.log(`[API Gateway] Routing ${req.method} ${req.originalUrl} -> Registration Service (${REGISTRATION_SERVICE})`);
  proxy.web(req, res, { target: REGISTRATION_SERVICE });
});

// Task 6: Login Microservice Routing (Public)
app.use('/auth', (req, res) => {
  console.log(`[API Gateway] Routing ${req.method} ${req.originalUrl} -> Login Service (${LOGIN_SERVICE})`);
  proxy.web(req, res, { target: LOGIN_SERVICE });
});

// Task 8: Admin Microservice Routing (Protected - Admin Only)
app.use('/admin', verifyTokenAndRole('admin'), (req, res) => {
  console.log(
    `[API Gateway] Routing ${req.method} ${req.originalUrl} -> Admin Service (${ADMIN_SERVICE}) [Verified Admin: ${req.user.email}]`
  );
  proxy.web(req, res, { target: ADMIN_SERVICE });
});

// Task 9: User Microservice Routing (Protected - User Only)
app.use('/user', verifyTokenAndRole('user'), (req, res) => {
  console.log(
    `[API Gateway] Routing ${req.method} ${req.originalUrl} -> User Service (${USER_SERVICE}) [Verified User: ${req.user.email}]`
  );
  proxy.web(req, res, { target: USER_SERVICE });
});

// Fallback for unmatched routes
app.use((req, res) => {
  res.status(404).json({
    error: 'Endpoint not found on API Gateway.'
  });
});

app.listen(PORT, () => {
  console.log(`====================================================`);
  console.log(`API Gateway running on Port: ${PORT}`);
  console.log(`Single Entry Point: http://localhost:${PORT}`);
  console.log(`====================================================`);
});
