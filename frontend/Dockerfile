# Build Stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

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