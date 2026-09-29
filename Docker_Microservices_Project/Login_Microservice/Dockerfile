# ==============================================================================
# Dockerfile: Login Microservice
# Multi-stage lightweight Node.js runtime environment
# ==============================================================================

FROM node:20-alpine

# Set working directory inside the container
WORKDIR /app

# Copy dependency manifests first to leverage Docker cache layers
COPY package*.json ./

# Install only production dependencies
RUN npm install --omit=dev

# Copy application source code
COPY . .

# Expose microservice port (Port 5002)
EXPOSE 5002

# Health check to ensure microservice readiness
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:5002/health || exit 1

# Start microservice
CMD ["node", "index.js"]
