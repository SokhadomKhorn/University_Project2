const express = require('express');
const cors = require('cors');
const connectDB = require('./db');
const User = require('./models/User');

const app = express();
const PORT = process.env.PORT || 5004;

// Middleware
app.use(cors());
app.use(express.json());

// Connect Database
connectDB();

// Health Check
app.get('/health', (req, res) => {
  res.json({ service: 'User Microservice', status: 'Active', port: PORT });
});

// Helper to resolve user identifier from headers or request
const resolveUserIdentifier = (req) => {
  return {
    userId: req.headers['x-user-id'] || (req.user && req.user.userId) || req.query.userId || (req.body && req.body.userId),
    userEmail: req.headers['x-user-email'] || (req.user && req.user.email) || req.query.email || (req.body && req.body.email)
  };
};

// 1. View Profile API: GET /user/viewprofile
const handleViewProfile = async (req, res) => {
  try {
    const { userId, userEmail } = resolveUserIdentifier(req);

    let query = {};
    if (userId) {
      query = { _id: userId };
    } else if (userEmail) {
      query = { email: userEmail.toLowerCase().trim() };
    } else {
      return res.status(400).json({
        error: 'Unable to identify user. Missing user credentials in headers/request.'
      });
    }

    const user = await User.findOne(query).select('-password');
    if (!user) {
      return res.status(404).json({
        error: 'User profile not found in database.'
      });
    }

    console.log(`[User Service] Profile retrieved for: ${user.email}`);
    return res.status(200).json({
      message: 'User profile retrieved successfully',
      profile: user
    });
  } catch (error) {
    console.error('[User Service] View Profile Error:', error.message);
    return res.status(500).json({
      error: 'Internal Server Error while retrieving profile',
      details: error.message
    });
  }
};

// 2. Update Profile API: PUT /user/updateprofile
const handleUpdateProfile = async (req, res) => {
  try {
    const { userId, userEmail } = resolveUserIdentifier(req);
    const { name, phone } = req.body;

    let query = {};
    if (userId) {
      query = { _id: userId };
    } else if (userEmail) {
      query = { email: userEmail.toLowerCase().trim() };
    } else {
      return res.status(400).json({
        error: 'Unable to identify user. Missing user credentials in headers/request.'
      });
    }

    const updateData = {};
    if (name) updateData.name = name.trim();
    if (phone) updateData.phone = phone.trim();

    if (Object.keys(updateData).length === 0) {
      return res.status(400).json({
        error: 'Please provide at least one field to update (name or phone).'
      });
    }

    const updatedUser = await User.findOneAndUpdate(
      query,
      { $set: updateData },
      { new: true, runValidators: true }
    ).select('-password');

    if (!updatedUser) {
      return res.status(404).json({
        error: 'User profile not found. Cannot update.'
      });
    }

    console.log(`[User Service] Profile updated successfully for: ${updatedUser.email}`);
    return res.status(200).json({
      message: 'User profile updated successfully',
      updatedProfile: updatedUser
    });
  } catch (error) {
    console.error('[User Service] Update Profile Error:', error.message);
    return res.status(500).json({
      error: 'Internal Server Error while updating profile',
      details: error.message
    });
  }
};

// Register Routes (both prefixed and direct)
app.get('/user/viewprofile', handleViewProfile);
app.get('/viewprofile', handleViewProfile);

app.put('/user/updateprofile', handleUpdateProfile);
app.put('/updateprofile', handleUpdateProfile);

app.listen(PORT, () => {
  console.log(`User Microservice running on Port: ${PORT}`);
});
