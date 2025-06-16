# Step 1: Build the React/Vite app
FROM node:20 AS builder

WORKDIR /app

# Install deps before copying source for better caching
COPY package*.json ./

# Avoid optional native binaries issues
RUN npm install --omit=optional

COPY . .

RUN npm run build

# Step 2: Serve using Nginx
FROM nginx:alpine

# Remove default nginx page
RUN rm -rf /usr/share/nginx/html/*

# Copy built frontend from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx config if any
# COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]