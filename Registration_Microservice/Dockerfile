# Use official lightweight Node.js 18 LTS Alpine base image
FROM node:18-alpine

# Set working directory inside the container
WORKDIR /usr/src/app

# Copy package definition files
COPY package*.json ./

# Install application dependencies (omit development packages)
RUN npm install --production

# Copy application source code into the container
COPY . .

# Expose Registration Microservice port
EXPOSE 5001

# Set production environment variables
ENV PORT=5001
ENV NODE_ENV=production

# Health check to ensure microservice is operational
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:5001/health || exit 1

# Start the Registration Microservice
CMD ["node", "index.js"]
