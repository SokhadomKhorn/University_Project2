const express = require('express');
const bcrypt = require('bcryptjs');
const cors = require('cors');
const connectDB = require('./db');
const User = require('./models/User');

const app = express();
const PORT = process.env.PORT || 5001;

// Middleware
app.use(cors());
app.use(express.json());

// Connect Database
connectDB();

// Health Check
app.get('/health', (req, res) => {
  res.json({ service: 'Registration Microservice', status: 'Active', port: PORT });
});

// Registration API Handler
const handleRegistration = async (req, res) => {
  try {
    // 1. Extract and normalize fields (support standard names and person_* aliases)
    const rawName = req.body.name || req.body.person_name;
    const rawEmail = req.body.email || req.body.person_email;
    const rawPassword = req.body.password || req.body.person_password;
    const rawRole = req.body.role || req.body.person_role || 'user';
    const rawPhone = req.body.phone || req.body.person_phone || '000-000-0000';

    if (!rawName || !rawEmail || !rawPassword) {
      return res.status(400).json({
        error: 'Validation Failed: name, email, and password are required.'
      });
    }

    // Validate role if provided
    const userRole = rawRole.toLowerCase();
    if (!['admin', 'user'].includes(userRole)) {
      return res.status(400).json({
        error: "Validation Failed: role must be either 'admin' or 'user'."
      });
    }

    // 2. Check duplicate email in MongoDB
    const normalizedEmail = rawEmail.toLowerCase().trim();
    const existingUser = await User.findOne({ email: normalizedEmail });
    if (existingUser) {
      return res.status(400).json({
        error: 'Duplicate Email: An account with this email address already exists.'
      });
    }

    // 3. Hash password using bcrypt
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(rawPassword, salt);

    // 4. Create and persist user in MongoDB
    const newUser = new User({
      name: rawName.trim(),
      email: normalizedEmail,
      password: hashedPassword,
      role: userRole,
      phone: rawPhone.trim()
    });

    const savedUser = await newUser.save();

    console.log(`[Registration Service] New user registered successfully: ${savedUser.email} (${savedUser.role})`);

    // 5. Return success response with sanitized user data
    return res.status(201).json({
      message: 'User registered successfully',
      user: {
        _id: savedUser._id,
        name: savedUser.name,
        email: savedUser.email,
        role: savedUser.role,
        phone: savedUser.phone,
        createdAt: savedUser.createdAt,
        updatedAt: savedUser.updatedAt
      }
    });
  } catch (error) {
    console.error('[Registration Service] Error:', error.message);
    return res.status(500).json({
      error: 'Internal Server Error during registration',
      details: error.message
    });
  }
};

// Route handlers for direct or proxied access
app.post('/register/userregister', handleRegistration);
app.post('/userregister', handleRegistration);
app.post('/register', handleRegistration);
app.post('/reg', handleRegistration);

app.listen(PORT, () => {
  console.log(`Registration Microservice running on Port: ${PORT}`);
});
