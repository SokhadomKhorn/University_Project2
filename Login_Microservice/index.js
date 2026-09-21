const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const cors = require('cors');
const connectDB = require('./db');
const User = require('./models/User');

const app = express();
const PORT = process.env.PORT || 5002;
const JWT_SECRET = process.env.JWT_SECRET || 'UniversitySecretKey2026';

// Middleware
app.use(cors());
app.use(express.json());

// Connect Database
connectDB();

// Health Check
app.get('/health', (req, res) => {
  res.json({ service: 'Login Microservice', status: 'Active', port: PORT });
});

// Login API Handler
const handleLogin = async (req, res) => {
  try {
    const { email, password, role } = req.body;

    // 1. Validate inputs
    if (!email || !password || !role) {
      return res.status(400).json({
        error: 'Validation Error: email, password, and role are all required.'
      });
    }

    const normalizedEmail = email.toLowerCase().trim();
    const normalizedRole = role.toLowerCase().trim();

    if (!['admin', 'user'].includes(normalizedRole)) {
      return res.status(400).json({
        error: "Invalid role specified. Role must be 'admin' or 'user'."
      });
    }

    // 2. Find user in MongoDB
    const user = await User.findOne({ email: normalizedEmail });
    if (!user) {
      return res.status(401).json({
        error: 'Invalid Email or Password or role'
      });
    }

    // 3. Validate Role match
    if (user.role.toLowerCase() !== normalizedRole) {
      console.log(`[Login Service] Role mismatch for ${normalizedEmail}. Given: ${normalizedRole}, Expected: ${user.role}`);
      return res.status(401).json({
        error: 'Invalid Email or Password or role'
      });
    }

    // 4. Validate Password match using bcrypt
    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      console.log(`[Login Service] Password mismatch for ${normalizedEmail}`);
      return res.status(401).json({
        error: 'Invalid Email or Password or role'
      });
    }

    // 5. Generate JWT Token with payload: userId, email, role
    const tokenPayload = {
      userId: user._id,
      email: user.email,
      role: user.role
    };

    const token = jwt.sign(tokenPayload, JWT_SECRET, {
      expiresIn: '2h'
    });

    console.log(`[Login Service] User authenticated successfully: ${user.email} as [${user.role}]`);

    // 6. Return JWT and sanitized user info
    return res.status(200).json({
      message: 'Login successful',
      token: token,
      user: {
        _id: user._id,
        name: user.name,
        email: user.email,
        role: user.role,
        phone: user.phone
      }
    });
  } catch (error) {
    console.error('[Login Service] Error:', error.message);
    return res.status(500).json({
      error: 'Internal Server Error during login',
      details: error.message
    });
  }
};

// Route handlers (both /auth/login and /login for direct or proxied access)
app.post('/auth/login', handleLogin);
app.post('/login', handleLogin);

app.listen(PORT, () => {
  console.log(`Login Microservice running on Port: ${PORT}`);
});
