#!/bin/sh

# Docker entrypoint script for production web deployment
set -e

echo "Starting web application deployment..."

# Function to wait for backend service
wait_for_backend() {
    local backend_host=${BACKEND_HOST:-api_gateway}
    local backend_port=${BACKEND_PORT:-8080}
    local max_attempts=30
    local attempt=1
    
    echo "Waiting for backend service at $backend_host:$backend_port..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z "$backend_host" "$backend_port" 2>/dev/null; then
            echo "Backend service is available!"
            return 0
        fi
        
        echo "Attempt $attempt/$max_attempts: Backend not ready, waiting 5 seconds..."
        sleep 5
        attempt=$((attempt + 1))
    done
    
    echo "Warning: Backend service not available after $max_attempts attempts"
    echo "Continuing with nginx startup..."
    return 1
}

# Function to configure nginx based on environment
configure_nginx() {
    local nginx_conf="/etc/nginx/nginx.conf"
    local backend_host=${BACKEND_HOST:-api_gateway}
    local backend_port=${BACKEND_PORT:-8080}
    
    echo "Configuring nginx for backend: $backend_host:$backend_port"
    
    # Replace backend server configuration if needed
    if [ -f "/etc/nginx/nginx.conf.template" ]; then
        envsubst '${BACKEND_HOST} ${BACKEND_PORT}' < /etc/nginx/nginx.conf.template > "$nginx_conf"
    fi
    
    # Test nginx configuration
    nginx -t
    if [ $? -ne 0 ]; then
        echo "Error: nginx configuration test failed"
        exit 1
    fi
    
    echo "Nginx configuration is valid"
}

# Function to check if we're in production mode
is_production() {
    [ "${NODE_ENV:-production}" = "production" ]
}

# Main execution
main() {
    echo "Environment: ${NODE_ENV:-production}"
    echo "Backend URL: ${BACKEND_URL:-http://api_gateway:8080}"
    
    # Wait for backend in production
    if is_production; then
        wait_for_backend
    fi
    
    # Configure nginx
    configure_nginx
    
    # Start nginx
    echo "Starting nginx..."
    exec nginx -g "daemon off;"
}

# Run main function
main "$@"
