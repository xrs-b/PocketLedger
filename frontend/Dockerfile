# Frontend Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code (只复制 frontend 目录)
COPY frontend/ .

# Build the application
RUN npm run build

# Production stage with Nginx
FROM nginx:alpine

# Copy built assets (dist 在 /app/dist)
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration (nginx.conf 在 /app/nginx.conf)
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
