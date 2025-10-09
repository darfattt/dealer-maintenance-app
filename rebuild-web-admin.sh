#!/bin/bash
# Quick rebuild script for web admin application
# This rebuilds the Docker container to reflect code changes

echo "🚀 Rebuilding Web Admin Application..."
echo

# Stop and remove current container
echo "Stopping current container..."
docker stop dealer_web_admin 2>/dev/null
docker rm dealer_web_admin 2>/dev/null

# Rebuild with no cache
echo "Building new image..."
docker-compose build --no-cache web_admin

# Start container
echo "Starting container..."
docker-compose up -d web_admin

# Show status
echo
echo "Container status:"
docker ps --filter "name=dealer_web_admin"

echo
echo "✅ Done! Access your app at http://localhost:5001"
echo