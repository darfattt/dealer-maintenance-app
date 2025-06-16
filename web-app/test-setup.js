#!/usr/bin/env node

/**
 * Simple setup test script for the Vue 3 web application
 * Tests basic functionality and dependencies
 */

const fs = require('fs')
const path = require('path')
const { execSync } = require('child_process')

console.log('🧪 Testing Vue 3 Web Application Setup...\n')

// Test 1: Check Node.js version
console.log('1. Checking Node.js version...')
try {
  const nodeVersion = process.version
  const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0])
  
  if (majorVersion >= 18) {
    console.log(`   ✅ Node.js ${nodeVersion} (>= 18.0.0)`)
  } else {
    console.log(`   ❌ Node.js ${nodeVersion} (< 18.0.0) - Please upgrade`)
    process.exit(1)
  }
} catch (error) {
  console.log(`   ❌ Error checking Node.js: ${error.message}`)
  process.exit(1)
}

// Test 2: Check required files
console.log('\n2. Checking required files...')
const requiredFiles = [
  'package.json',
  'vite.config.js',
  'index.html',
  'src/main.js',
  'src/App.vue',
  'src/router/index.js',
  'src/stores/auth.js',
  'src/views/LoginView.vue',
  'src/views/DashboardView.vue',
  'src/components/layout/AppTopbar.vue',
  'src/components/layout/AppSidebar.vue',
  'src/components/layout/AppMenu.vue'
]

let missingFiles = []
requiredFiles.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`   ✅ ${file}`)
  } else {
    console.log(`   ❌ ${file} - Missing`)
    missingFiles.push(file)
  }
})

if (missingFiles.length > 0) {
  console.log(`\n❌ Missing ${missingFiles.length} required files`)
  process.exit(1)
}

// Test 3: Check package.json dependencies
console.log('\n3. Checking package.json dependencies...')
try {
  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'))
  const requiredDeps = [
    'vue',
    'vue-router', 
    'pinia',
    'primevue',
    'primeicons',
    'primeflex',
    'axios'
  ]
  
  requiredDeps.forEach(dep => {
    if (packageJson.dependencies[dep]) {
      console.log(`   ✅ ${dep}: ${packageJson.dependencies[dep]}`)
    } else {
      console.log(`   ❌ ${dep} - Missing from dependencies`)
      process.exit(1)
    }
  })
} catch (error) {
  console.log(`   ❌ Error reading package.json: ${error.message}`)
  process.exit(1)
}

// Test 4: Check if node_modules exists
console.log('\n4. Checking node_modules...')
if (fs.existsSync('node_modules')) {
  console.log('   ✅ node_modules directory exists')
  
  // Check if key packages are installed
  const keyPackages = ['vue', 'primevue', 'axios']
  keyPackages.forEach(pkg => {
    if (fs.existsSync(`node_modules/${pkg}`)) {
      console.log(`   ✅ ${pkg} installed`)
    } else {
      console.log(`   ❌ ${pkg} not installed`)
    }
  })
} else {
  console.log('   ⚠️  node_modules not found - run "npm install"')
}

// Test 5: Check environment configuration
console.log('\n5. Checking environment configuration...')
if (fs.existsSync('.env.example')) {
  console.log('   ✅ .env.example exists')
} else {
  console.log('   ❌ .env.example missing')
}

if (fs.existsSync('.env')) {
  console.log('   ✅ .env exists')
} else {
  console.log('   ⚠️  .env not found - will use defaults')
}

// Test 6: Validate Vue component syntax
console.log('\n6. Validating Vue component syntax...')
try {
  const appVue = fs.readFileSync('src/App.vue', 'utf8')
  if (appVue.includes('<template>') && appVue.includes('<script setup>')) {
    console.log('   ✅ App.vue has valid Vue 3 Composition API syntax')
  } else {
    console.log('   ❌ App.vue missing required Vue 3 syntax')
  }
  
  const loginVue = fs.readFileSync('src/views/LoginView.vue', 'utf8')
  if (loginVue.includes('useAuthStore')) {
    console.log('   ✅ LoginView.vue uses Pinia store')
  } else {
    console.log('   ❌ LoginView.vue missing Pinia store usage')
  }
} catch (error) {
  console.log(`   ❌ Error validating Vue components: ${error.message}`)
}

// Test 7: Check Docker configuration
console.log('\n7. Checking Docker configuration...')
if (fs.existsSync('Dockerfile')) {
  console.log('   ✅ Dockerfile exists')
} else {
  console.log('   ❌ Dockerfile missing')
}

if (fs.existsSync('nginx.conf')) {
  console.log('   ✅ nginx.conf exists')
} else {
  console.log('   ❌ nginx.conf missing')
}

// Test 8: Check if backend services are accessible (optional)
console.log('\n8. Checking backend services (optional)...')
try {
  // This is optional - services might not be running during setup
  const http = require('http')
  
  const checkService = (port, name) => {
    return new Promise((resolve) => {
      const req = http.get(`http://localhost:${port}/health`, (res) => {
        if (res.statusCode === 200) {
          console.log(`   ✅ ${name} (port ${port}) is accessible`)
        } else {
          console.log(`   ⚠️  ${name} (port ${port}) returned status ${res.statusCode}`)
        }
        resolve()
      })
      
      req.on('error', () => {
        console.log(`   ⚠️  ${name} (port ${port}) not accessible (service may not be running)`)
        resolve()
      })
      
      req.setTimeout(2000, () => {
        console.log(`   ⚠️  ${name} (port ${port}) timeout (service may not be running)`)
        req.destroy()
        resolve()
      })
    })
  }
  
  Promise.all([
    checkService(8080, 'API Gateway'),
    checkService(8100, 'Account Service')
  ]).then(() => {
    console.log('\n🎉 Setup test completed!')
    console.log('\n📋 Next steps:')
    console.log('   1. Install dependencies: npm install')
    console.log('   2. Start backend services: docker-compose up -d postgres account_service api_gateway')
    console.log('   3. Start web app: npm run dev')
    console.log('   4. Open browser: http://localhost:3000')
    console.log('   5. Login with: admin@dealer-dashboard.com / Admin123!')
  })
  
} catch (error) {
  console.log('   ⚠️  Could not check backend services')
  console.log('\n🎉 Setup test completed!')
}
