const mongoose = require('mongoose');
const path = require('path');
const dns = require('dns');

// Configure public DNS servers for fast and reliable MongoDB Atlas SRV resolution
try {
  dns.setServers(['8.8.8.8', '1.1.1.1', '8.8.4.4']);
} catch (e) {
  // Ignore if not permitted
}

require('dotenv').config({ path: path.resolve(__dirname, '..', '.env') });
require('dotenv').config();

const connectDB = async () => {
  try {
    const mongoURI = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/university_identity_db';
    const conn = await mongoose.connect(mongoURI, {
      serverSelectionTimeoutMS: 5000
    });
    console.log(`[DBConnect] MongoDB Connected successfully to: ${conn.connection.host}/${conn.connection.name}`);
    return conn;
  } catch (error) {
    console.error(`[DBConnect] MongoDB Connection Error: ${error.message}`);
  }
};

module.exports = connectDB;
