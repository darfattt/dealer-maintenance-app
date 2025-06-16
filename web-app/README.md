# Dealer Dashboard Web Application

A modern Vue 3 web application using Sakai PrimeVue admin template with authentication and minimal features.

## 🚀 Features

- **Vue 3** with Composition API
- **Sakai PrimeVue** admin template
- **JWT Authentication** with automatic token refresh
- **Pinia** for state management
- **Vue Router** for navigation
- **Axios** for API communication
- **Responsive Design** with mobile support
- **Clean Architecture** with minimal features

## 🏗️ Architecture

```
web-app/
├── src/
│   ├── components/
│   │   └── layout/          # Layout components (Topbar, Sidebar, Menu)
│   ├── views/               # Page components
│   ├── stores/              # Pinia stores
│   ├── services/            # API services
│   ├── assets/              # Static assets and styles
│   └── router/              # Vue Router configuration
├── public/                  # Public assets
└── dist/                    # Build output
```

## 🔧 Setup

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend microservices running (Account Service on port 8100, API Gateway on port 8080)

### Installation

1. **Install dependencies:**
   ```bash
   cd web-app
   npm install
   ```

2. **Environment configuration:**
   ```bash
   cp .env.example .env
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Access the application:**
   - Web App: http://localhost:3000
   - Login with: admin@dealer-dashboard.com / Admin123!

## 🔐 Authentication

The application uses JWT-based authentication with the following features:

- **Login/Logout** functionality
- **Automatic token refresh** when tokens expire
- **Route protection** for authenticated users only
- **Persistent sessions** using localStorage
- **Role-based access** (SUPER_ADMIN, DEALER_ADMIN)

### Default Credentials

- **Email:** admin@dealer-dashboard.com
- **Password:** Admin123!

## 🎨 UI Components

Based on Sakai PrimeVue template with:

- **Clean Layout** with top navigation and left sidebar
- **Responsive Design** for mobile and desktop
- **Minimal Menu** with Home > Dashboard only
- **Modern Styling** using PrimeFlex and custom SCSS
- **Toast Notifications** for user feedback
- **Loading States** and error handling

## 🌐 API Integration

Connects to backend microservices through:

- **API Gateway** (http://localhost:8080) for authentication
- **Account Service** (http://localhost:8100) for user management
- **Automatic proxy** configuration in Vite for development

## 📱 Navigation Structure

```
Home
└── Dashboard (/)
```

Simple navigation following the requirement for minimal features with only Home > Dashboard menu structure.

## 🔗 External Links

The dashboard provides quick access to:

- **Analytics Dashboard** (http://localhost:8501) - Streamlit analytics
- **Admin Panel** (http://localhost:8502) - Streamlit admin interface  
- **API Documentation** (http://localhost:8000/docs) - FastAPI docs

## 🛠️ Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

### Code Structure

- **Composition API** for reactive components
- **Pinia stores** for state management
- **Modular components** for maintainability
- **SCSS styling** with CSS variables
- **TypeScript ready** (can be added later)

## 🚀 Deployment

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Serve the dist folder** using any static file server

3. **Configure proxy** for API calls in production

## 🔧 Configuration

### Environment Variables

- `VITE_API_BASE_URL` - Backend API base URL
- `VITE_API_TIMEOUT` - API request timeout
- `VITE_APP_TITLE` - Application title
- `VITE_ANALYTICS_URL` - Analytics dashboard URL
- `VITE_ADMIN_PANEL_URL` - Admin panel URL

### Proxy Configuration

Development proxy is configured in `vite.config.js` to forward `/api` requests to the API Gateway on port 8080.

## 📋 Requirements Met

✅ **Vue 3** framework  
✅ **Sakai PrimeVue** admin template  
✅ **Authentication** with JWT  
✅ **Minimal features** and clean format  
✅ **Top menu** following Sakai framework  
✅ **Left menu** with Home > Dashboard only  
✅ **Backend integration** with microservices  

## 🤝 Contributing

1. Follow Vue 3 Composition API patterns
2. Use PrimeVue components consistently
3. Maintain clean, minimal design
4. Test authentication flows
5. Ensure responsive design

## 📄 License

This project is part of the Dealer Dashboard system.
