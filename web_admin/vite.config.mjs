import { fileURLToPath, URL } from 'node:url';

import { PrimeVueResolver } from '@primevue/auto-import-resolver';
import vue from '@vitejs/plugin-vue';
import Components from 'unplugin-vue-components/vite';
import { defineConfig } from 'vite';

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
    const isDev = command === 'serve';
    const isProd = mode === 'production';

    return {
        optimizeDeps: {
            noDiscovery: true
        },
        plugins: [
            vue(),
            Components({
                resolvers: [PrimeVueResolver()]
            })
        ],
        resolve: {
            alias: {
                '@': fileURLToPath(new URL('./src', import.meta.url))
            }
        },
        build: {
            outDir: 'dist',
            sourcemap: !isProd,
            minify: isProd ? 'esbuild' : false,
            rollupOptions: {
                output: {
                    manualChunks: {
                        vendor: ['vue', 'vue-router', 'pinia'],
                        primevue: ['primevue/config', 'primevue/button', 'primevue/inputtext', 'primevue/password']
                    }
                }
            }
        },
        server: isDev
            ? {
                  host: '0.0.0.0',
                  port: 5174,
                  proxy: {
                      '/api': {
                          // Use Docker service name when in container, localhost for local dev
                          target: process.env.DOCKER_ENV ? 'http://api_gateway:8080' : process.env.VITE_API_BASE_URL || 'http://localhost:8080',
                          changeOrigin: true,
                          secure: false,
                          // Don't rewrite the path - preserve full /api/v1/... path
                          rewrite: (path) => path,
                          configure: (proxy, options) => {
                              proxy.on('error', (err, req, res) => {
                                  console.log('proxy error', err);
                              });
                              proxy.on('proxyReq', (proxyReq, req, res) => {
                                  console.log('Sending Request to the Target:', req.method, req.url, '-> Full URL:', proxyReq.path);
                              });
                              proxy.on('proxyRes', (proxyRes, req, res) => {
                                  console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
                              });
                          }
                      }
                  }
              }
            : {}
    };
});
