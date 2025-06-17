# Web Application Setup - Vue 3 with PrimeVue

## Overview

This document describes the setup and configuration of the Vue 3 web application using PrimeVue components and Sakai template for the dealer dashboard system.

## Application Structure

### Technology Stack
- **Frontend Framework**: Vue 3 with Composition API
- **UI Library**: PrimeVue 4.x with Sakai template
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with PrimeUI
- **Icons**: PrimeIcons
- **Authentication**: JWT-based with API integration
- **Deployment**: Docker with Nginx (production) and Vite dev server (development)

### Project Structure
```
web/
├── src/
│   ├── components/          # Reusable Vue components
│   ├── views/              # Page components
│   │   ├── pages/
│   │   │   └── auth/
│   │   │       └── Login.vue
│   │   └── Dashboard.vue
│   ├── router/             # Vue Router configuration
│   ├── stores/             # Pinia state management
│   ├── services/           # API service layer
│   ├── utils/              # Utility functions
│   └── assets/             # Static assets
├── public/                 # Public static files
├── package.json            # Dependencies and scripts
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind CSS configuration
├── Dockerfile              # Multi-stage Docker build
└── nginx.conf              # Nginx configuration for production
```

## Docker Configuration

### Multi-Stage Dockerfile
The application uses a multi-stage Docker build with three targets:

1. **Base Stage**: Node.js 18 Alpine base image
2. **Development Stage**: Vite dev server with hot reload
3. **Production Stage**: Nginx serving built static files

### Environment Variables
- `NODE_ENV`: development/production
- `VITE_API_BASE_URL`: Backend API base URL

## Deployment Options

### Production Deployment (Port 5000)
```bash
# Build and run production container
docker-compose build web_primevue
docker-compose up web_primevue -d

# Access application
http://localhost:5000
```

### Development Environment (Port 5173)
```bash
# Create network if not exists
docker network create dealer-network

# Run development server with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up web_app -d

# Access development server
http://localhost:5173
```

## Features Implemented

### Authentication System
- JWT-based authentication
- Login form with validation
- Token storage and management
- Protected routes with navigation guards
- Automatic token refresh

### UI Components
- Responsive layout with sidebar navigation
- PrimeVue components integration
- Sakai template styling
- Dark/light theme support
- Mobile-responsive design

### API Integration
- Axios-based HTTP client
- Request/response interceptors
- Error handling
- Authentication headers

## Configuration Files

### Vite Configuration (`vite.config.js`)
- Vue 3 plugin setup
- Development server configuration
- Build optimization
- Environment variable handling

### Tailwind Configuration (`tailwind.config.js`)
- PrimeUI integration
- Custom color schemes
- Responsive breakpoints

### Nginx Configuration (`nginx.conf`)
- Single Page Application routing
- Static file serving
- Gzip compression
- Security headers

## Development Workflow

### Local Development
1. Start backend services: `docker-compose up postgres account_service api_gateway -d`
2. Start development web server: `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up web_app -d`
3. Access application at `http://localhost:5173`
4. Make changes to source files - hot reload will update automatically

### Production Build
1. Build production image: `docker-compose build web_primevue`
2. Deploy production container: `docker-compose up web_primevue -d`
3. Access application at `http://localhost:5000`

## Testing

### Manual Testing
- Login functionality with valid/invalid credentials
- Navigation between pages
- Responsive design on different screen sizes
- API integration with backend services

### Browser Compatibility
- Modern browsers supporting ES6+
- Mobile browsers (iOS Safari, Chrome Mobile)
- Desktop browsers (Chrome, Firefox, Safari, Edge)

## Security Considerations

### Authentication
- JWT tokens stored securely
- Automatic token expiration handling
- Protected API endpoints
- CSRF protection

### Production Security
- Nginx security headers
- Content Security Policy
- HTTPS ready configuration
- Static file optimization

## Troubleshooting

### Common Issues
1. **Port conflicts**: Ensure ports 5000 and 5173 are available
2. **Network issues**: Create `dealer-network` if using development compose
3. **Build failures**: Check Node.js version compatibility
4. **API connection**: Verify backend services are running

### Logs
```bash
# View container logs
docker logs dealer_web_primevue
docker logs dealer_web_app_dev

# Follow logs in real-time
docker logs -f dealer_web_primevue
```

## Next Steps

### Planned Enhancements
1. User management interface
2. Dashboard analytics
3. Real-time notifications
4. Advanced routing
5. State persistence
6. Offline support
7. Progressive Web App features

### Performance Optimization
1. Code splitting
2. Lazy loading
3. Image optimization
4. Bundle analysis
5. Caching strategies

## Maintenance

### Updates
- Regular dependency updates
- Security patches
- PrimeVue version updates
- Vue 3 ecosystem updates

### Monitoring
- Application performance
- Error tracking
- User analytics
- API response times
