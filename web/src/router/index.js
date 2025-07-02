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
                    name: 'dashboard',
                    component: () => import('@/views/Dashboard.vue')
                },
                {
                    path: '/prospecting-activity',
                    name: 'prospecting-activity',
                    component: () => import('@/views/ProspectingActivity.vue')
                },
                {
                    path: '/dealing-process',
                    name: 'dealing-process',
                    component: () => import('@/views/DealingProcess.vue')
                },
                {
                    path: '/delivery-process-detail',
                    name: 'delivery-process-detail',
                    component: () => import('@/views/DeliveryProcessDetail.vue')
                },
                {
                    path: '/unit-inbound-detail',
                    name: 'unit-inbound-detail',
                    component: () => import('@/views/UnitInboundDetail.vue')
                },
                {
                    path: '/payment-type-detail',
                    name: 'payment-type-detail',
                    component: () => import('@/views/PaymentTypeDetail.vue')
                },
                {
                    path: '/handle-leasing-detail',
                    name: 'handle-leasing-detail',
                    component: () => import('@/views/HandleLeasingDetail.vue')
                },
                {
                    path: '/document-handling-detail',
                    name: 'document-handling-detail',
                    component: () => import('@/views/DocumentHandlingDetail.vue')
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
            path: '/pages/notfound',
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
    const publicRoutes = ['/auth/login', '/auth/access', '/auth/error', '/pages/notfound'];

    if (publicRoutes.includes(to.path)) {
        // If user is already authenticated and trying to access login, redirect to dashboard
        if (to.path === '/auth/login' && authStore.isAuthenticated) {
            next('/');
        } else {
            next();
        }
    } else {
        // Protected routes - require authentication
        if (authStore.isAuthenticated) {
            next();
        } else {
            console.log('User not authenticated, redirecting to login from:', to.path);
            next('/auth/login');
        }
    }
});

export default router;
