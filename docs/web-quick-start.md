# Web Application Quick Start Guide

## Prerequisites
- Docker and Docker Compose installed
- Ports 5000 and 5173 available
- Backend services running (postgres, account_service, api_gateway)

## Quick Commands

### Production Environment
```bash
# Build and start production web app (Port 5000)
docker-compose build web_primevue
docker-compose up web_primevue -d

# Access application
open http://localhost:5000

# View logs
docker logs -f dealer_web_primevue

# Stop
docker-compose stop web_primevue
```

### Development Environment
```bash
# Create network (one-time setup)
docker network create dealer-network

# Start development server (Port 5173)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up web_app -d

# Access development server
open http://localhost:5173

# View logs
docker logs -f dealer_web_app_dev

# Stop
docker-compose -f docker-compose.yml -f docker-compose.dev.yml stop web_app
```

### Full System Startup
```bash
# Start all services including web app
docker-compose up -d

# Check status
docker ps

# View all logs
docker-compose logs -f
```

## Default Login Credentials
- **Email**: admin@dealer-dashboard.com
- **Password**: Admin123!

## Key URLs
- **Production Web App**: http://localhost:5000
- **Development Web App**: http://localhost:5173
- **API Gateway**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs

## File Structure
```
web/
├── src/
│   ├── views/pages/auth/Login.vue    # Login page
│   ├── views/Dashboard.vue           # Main dashboard
│   ├── router/index.js               # Routes
│   ├── stores/auth.js                # Authentication store
│   └── services/api.js               # API client
├── Dockerfile                        # Multi-stage build
├── package.json                      # Dependencies
└── vite.config.js                    # Vite config
```

## Development Tips

### Hot Reload
- Development server automatically reloads on file changes
- Edit files in `web/src/` directory
- Changes appear instantly in browser

### Debugging
```bash
# Enter development container
docker exec -it dealer_web_app_dev sh

# Check Vite dev server
curl http://localhost:5173

# View build output
npm run build
```

### Common Issues
1. **Port 5000 in use**: Stop other services or change port
2. **Network error**: Ensure `dealer-network` exists
3. **Build fails**: Check Node.js version in Dockerfile
4. **API errors**: Verify backend services are running

## Environment Variables
- `VITE_API_BASE_URL`: Backend API URL (default: http://localhost:8080)
- `NODE_ENV`: development/production

## Build Targets
- **development**: Vite dev server with hot reload
- **production**: Optimized build served by Nginx

## Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Next Steps
1. Customize login page styling
2. Add new pages and routes
3. Integrate with additional APIs
4. Implement user management
5. Add dashboard widgets
