#!/bin/bash

echo "Starting Dealer Dashboard Web Application..."
echo

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed or not in PATH"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

# Check if package.json exists
if [ ! -f package.json ]; then
    echo "Error: package.json not found"
    echo "Please run this script from the web-app directory"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d node_modules ]; then
    echo "Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
fi

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "Creating .env file from .env.example..."
        cp .env.example .env
    fi
fi

echo
echo "Starting development server..."
echo "Web App will be available at: http://localhost:3000"
echo
echo "Make sure the following services are running:"
echo "- API Gateway: http://localhost:8080"
echo "- Account Service: http://localhost:8100"
echo

# Start the development server
npm run dev
