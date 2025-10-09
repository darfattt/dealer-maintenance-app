import AppLayout from '@/layout/AppLayout.vue';
import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            component: AppLayout,
            children: [
                {
                    path: '/',
                    redirect: '/dealer-management'
                },
                {
                    path: '/dealer-management',
                    name: 'dealer-management',
                    component: () => import('@/views/DealerManagement.vue'),
                    meta: { requiresSystemAdmin: true }
                },
                {
                    path: '/dealer-management/register',
                    name: 'dealer-registration',
                    component: () => import('@/views/DealerRegistration.vue'),
                    meta: { requiresSystemAdmin: true }
                },
                {
                    path: '/system-logs/activities',
                    name: 'activities',
                    component: () => import('@/views/activities/Activities.vue'),
                    meta: { requiresSystemAdmin: true }
                },
                {
                    path: '/system-logs/summary',
                    name: 'summary',
                    component: () => import('@/views/summary/Summary.vue'),
                    meta: { requiresSystemAdmin: true }
                },
                {
                    path: '/anomalies',
                    name: 'anomalies',
                    component: () => import('@/views/anomalies/Anomalies.vue'),
                    meta: { requiresSystemAdmin: true }
                }
            ]
        },
        {
            path: '/auth/login',
            name: 'login',
            component: () => import('@/views/pages/auth/Login.vue')
        },
        {
            path: '/auth/access',
            name: 'accessDenied',
            component: () => import('@/views/pages/auth/Access.vue')
        },
        {
            path: '/auth/error',
            name: 'error',
            component: () => import('@/views/pages/auth/Error.vue')
        },
        {
            path: '/:pathMatch(.*)*',
            name: 'notfound',
            component: () => import('@/views/pages/NotFound.vue')
        }
    ]
});

// Authentication guard
router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();

    // Check authentication from localStorage
    authStore.checkAuth();

    // Routes that don't require authentication
    const publicRoutes = ['/auth/login', '/auth/access', '/auth/error'];

    if (publicRoutes.includes(to.path)) {
        // If user is already authenticated and trying to access login
        if (to.path === '/auth/login' && authStore.isAuthenticated) {
            // Check if user is SYSTEM_ADMIN
            if (authStore.userRole === 'SYSTEM_ADMIN') {
                next('/dealer-management');
            } else {
                // Not a SYSTEM_ADMIN, redirect to access denied
                next('/auth/access');
            }
        } else {
            next();
        }
    } else {
        // Protected routes - require authentication
        if (authStore.isAuthenticated) {
            // Check if route requires SYSTEM_ADMIN role
            if (to.meta.requiresSystemAdmin) {
                if (authStore.userRole === 'SYSTEM_ADMIN') {
                    next();
                } else {
                    console.log('Access denied: User is not SYSTEM_ADMIN');
                    next('/auth/access');
                }
            } else {
                next();
            }
        } else {
            console.log('User not authenticated, redirecting to login from:', to.path);
            next('/auth/login');
        }
    }
});

export default router;
