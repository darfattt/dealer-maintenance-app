# Vue 3 Web Application Setup Guide

This guide will help you set up and run the Vue 3 Dealer Dashboard web application.

## 🚀 Quick Start

### Option 1: Using Docker (Recommended)

1. **Start all services including web app:**
   ```bash
   # From the root directory (dealer-dashboard/)
   docker-compose up -d
   ```

2. **Access the web application:**
   - Web App: http://localhost:3000
   - Login: admin@dealer-dashboard.com / Admin123!

### Option 2: Development Mode

1. **Start backend services:**
   ```bash
   # From the root directory (dealer-dashboard/)
   docker-compose up -d postgres account_service api_gateway
   ```

2. **Start web app in development mode:**
   ```bash
   # Windows
   cd web-app
   start-dev.bat
   
   # Linux/Mac
   cd web-app
   chmod +x start-dev.sh
   ./start-dev.sh
   ```

3. **Access the application:**
   - Web App: http://localhost:3000
   - Hot reload enabled for development

## 📋 Prerequisites

### For Docker Setup
- Docker and Docker Compose
- Ports 3000, 8080, 8100, 5432 available

### For Development Setup
- Node.js 18+ 
- npm or yarn
- Backend services running (Account Service, API Gateway, PostgreSQL)

## 🔧 Manual Setup

### 1. Install Dependencies

```bash
cd web-app
npm install
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file if needed
# Default values should work for local development
```

### 3. Start Development Server

```bash
npm run dev
```

The application will be available at http://localhost:3000

## 🔐 Authentication

### Default Credentials
- **Email:** admin@dealer-dashboard.com
- **Password:** Admin123!

### Authentication Flow
1. Login page appears if not authenticated
2. JWT tokens stored in localStorage
3. Automatic token refresh on expiry
4. Logout clears all stored data

## 🌐 API Configuration

The web app connects to backend services through:

- **API Gateway:** http://localhost:8080 (proxied to `/api`)
- **Account Service:** http://localhost:8100 (via API Gateway)

### Development Proxy

Vite development server proxies `/api` requests to the API Gateway:

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true
    }
  }
}
```

## 🎨 UI Framework

### Sakai PrimeVue Template
- **PrimeVue 3.46+** components
- **PrimeFlex** for layout
- **PrimeIcons** for icons
- **Custom SCSS** styling

### Layout Structure
```
AppTopbar (Fixed top navigation)
├── Logo and title
├── Menu toggle (mobile)
└── User menu (Profile, Settings, Logout)

AppSidebar (Left navigation)
└── AppMenu
    └── Home
        └── Dashboard

Main Content Area
└── Router View (Dashboard, etc.)
```

## 📱 Responsive Design

- **Desktop:** Full sidebar and topbar
- **Mobile:** Collapsible sidebar with hamburger menu
- **Tablet:** Adaptive layout

## 🛠️ Development Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Format code
npm run format
```

## 🔗 External Links

The dashboard provides quick access to:

- **Analytics Dashboard:** http://localhost:8501
- **Admin Panel:** http://localhost:8502  
- **API Documentation:** http://localhost:8000/docs

## 🐛 Troubleshooting

### Common Issues

1. **Port 3000 already in use:**
   ```bash
   # Change port in vite.config.js or use different port
   npm run dev -- --port 3001
   ```

2. **API connection failed:**
   - Ensure API Gateway is running on port 8080
   - Check Account Service is running on port 8100
   - Verify PostgreSQL is running on port 5432

3. **Authentication not working:**
   - Check backend services are healthy
   - Verify default admin user exists in database
   - Check browser console for errors

4. **Build fails:**
   ```bash
   # Clear node_modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

### Service Health Check

```bash
# Check API Gateway
curl http://localhost:8080/health

# Check Account Service  
curl http://localhost:8100/api/v1/health

# Check if services are running
docker-compose ps
```

## 📦 Production Deployment

### Docker Production Build

```bash
# Build production image
docker build -t dealer-web-app .

# Run production container
docker run -p 3000:80 dealer-web-app
```

### Manual Production Build

```bash
# Build for production
npm run build

# Serve dist folder with any static file server
# Example with serve:
npx serve dist -p 3000
```

## 🔧 Configuration

### Environment Variables

- `VITE_API_BASE_URL` - Backend API URL
- `VITE_APP_TITLE` - Application title
- `VITE_ANALYTICS_URL` - Analytics dashboard URL
- `VITE_ADMIN_PANEL_URL` - Admin panel URL

### Nginx Configuration

For production deployment, the included `nginx.conf` provides:

- Client-side routing support
- API proxy configuration
- Static asset caching
- Security headers
- Gzip compression

## 📄 Project Structure

```
web-app/
├── src/
│   ├── components/layout/    # Layout components
│   ├── views/               # Page components  
│   ├── stores/              # Pinia stores
│   ├── services/            # API services
│   ├── assets/styles/       # SCSS styles
│   └── router/              # Vue Router
├── public/                  # Static assets
├── docker/                  # Docker configuration
└── dist/                    # Build output
```

## 🤝 Support

For issues or questions:

1. Check this setup guide
2. Review the main README.md
3. Check Docker logs: `docker-compose logs web_app`
4. Verify backend services are running
5. Check browser console for errors
