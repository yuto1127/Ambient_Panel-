# Build Stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Install gcc and other required packages
FROM python:3.11-slim

# Install system dependencies for building
RUN apk update && apk add --no-cache \
    gcc \
    g++ \
    make \
    i2c-tools \
    libi2c-dev && \
    rm -rf /var/lib/apt/lists/*

# Install required Python packages
WORKDIR /app
COPY requirements-pi.txt .
RUN pip install --no-cache-dir -r requirements-pi.txt

# Copy the application code
COPY . .

# Expose the port and define the entrypoint
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

# Copy the source code
COPY . .

# Build the application
RUN npm run build

# Production Stage
FROM nginx:alpine

# Copy the build files from the builder image
COPY --from=builder /app/dist /usr/share/nginx/html

# If you have a custom Nginx configuration, copy it (make sure the file exists)
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80 for the frontend
EXPOSE 80

# Run nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]
