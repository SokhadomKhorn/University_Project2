const express = require('express');
const cors = require('cors');
const connectDB = require('./db');
const User = require('./models/User');

const app = express();
const PORT = process.env.PORT || 5003;

// Middleware
app.use(cors());
app.use(express.json());

// Connect Database
connectDB();

// Health Check
app.get('/health', (req, res) => {
  res.json({ service: 'Admin Microservice', status: 'Active', port: PORT });
});

// 1. Search User API: GET /admin/searchuser
// Allows searching by ?email=..., ?name=..., or ?query=...
const handleSearchUser = async (req, res) => {
  try {
    const { name, email, query } = req.query;

    if (!name && !email && !query) {
      return res.status(400).json({
        error: 'Please provide name, email, or query parameter to search.'
      });
    }

    let filter = {};
    if (query) {
      filter = {
        $or: [
          { name: { $regex: query.trim(), $options: 'i' } },
          { email: { $regex: query.trim(), $options: 'i' } }
        ]
      };
    } else if (email && name) {
      filter = {
        $or: [
          { email: email.toLowerCase().trim() },
          { name: { $regex: name.trim(), $options: 'i' } }
        ]
      };
    } else if (email) {
      filter = { email: email.toLowerCase().trim() };
    } else if (name) {
      filter = { name: { $regex: name.trim(), $options: 'i' } };
    }

    const users = await User.find(filter).select('-password');

    if (!users || users.length === 0) {
      return res.status(404).json({
        message: 'User Not Found',
        error: 'No user found matching the provided search criteria.'
      });
    }

    console.log(`[Admin Service] Search completed: found ${users.length} match(es)`);
    return res.status(200).json({
      message: 'User found successfully',
      count: users.length,
      users: users
    });
  } catch (error) {
    console.error('[Admin Service] Search Error:', error.message);
    return res.status(500).json({
      error: 'Internal Server Error during user search',
      details: error.message
    });
  }
};

// 2. View All Users API: GET /admin/viewalluser
const handleViewAllUsers = async (req, res) => {
  try {
    const users = await User.find().select('-password').sort({ createdAt: -1 });

    console.log(`[Admin Service] View all users: retrieved ${users.length} user(s)`);
    return res.status(200).json({
      message: 'All users retrieved successfully',
      totalUsers: users.length,
      users: users
    });
  } catch (error) {
    console.error('[Admin Service] View All Error:', error.message);
    return res.status(500).json({
      error: 'Internal Server Error while retrieving users',
      details: error.message
    });
  }
};

// 3. Delete User API: DELETE /admin/deluser
// Supports email via query param (?email=...) or body ({ email: "..." })
const handleDeleteUser = async (req, res) => {
  try {
    const email = req.query.email || (req.body && req.body.email);

    if (!email) {
      return res.status(400).json({
        error: 'Validation Error: email is required to delete a user (pass via query or body).'
      });
    }

    const normalizedEmail = email.toLowerCase().trim();
    const deletedUser = await User.findOneAndDelete({ email: normalizedEmail }).select('-password');

    if (!deletedUser) {
      return res.status(404).json({
        message: 'User Not Found',
        error: `Cannot delete user: No account found with email '${normalizedEmail}'.`
      });
    }

    console.log(`[Admin Service] User deleted successfully: ${normalizedEmail}`);
    return res.status(200).json({
      message: `User with email '${normalizedEmail}' deleted successfully`,
      deletedUser: deletedUser
    });
  } catch (error) {
    console.error('[Admin Service] Delete Error:', error.message);
    return res.status(500).json({
      error: 'Internal Server Error while deleting user',
      details: error.message
    });
  }
};

// Register Routes (both prefixed and direct)
app.get('/admin/searchuser', handleSearchUser);
app.get('/searchuser', handleSearchUser);

app.get('/admin/viewalluser', handleViewAllUsers);
app.get('/viewalluser', handleViewAllUsers);

app.delete('/admin/deluser', handleDeleteUser);
app.delete('/deluser', handleDeleteUser);

app.listen(PORT, () => {
  console.log(`Admin Microservice running on Port: ${PORT}`);
});
