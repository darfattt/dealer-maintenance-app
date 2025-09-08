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
                    name: 'home',
                    component: () => import('@/views/CustomerValidationRequest.vue')
                },
                {
                    path: '/h1-dashboard',
                    name: 'h1-dashboard',
                    component: () => import('@/views/H1Dashboard.vue')
                },
                {
                    path: '/h23-dashboard',
                    name: 'h23-dashboard',
                    component: () => import('@/views/H23Dashboard.vue')
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
                    path: '/test-payment-status-widget',
                    name: 'test-payment-status-widget',
                    component: () => import('@/views/TestPaymentStatusWidget.vue')
                },
                {
                    path: '/test-payment-revenue-widget',
                    name: 'test-payment-revenue-widget',
                    component: () => import('@/views/test/PaymentRevenueTest.vue')
                },
                {
                    path: '/document-handling-detail',
                    name: 'document-handling-detail',
                    component: () => import('@/views/DocumentHandlingDetail.vue')
                },
                {
                    path: '/customer-validation',
                    name: 'customer-validation',
                    component: () => import('@/views/CustomerValidationRequest.vue')
                },
                {
                    path: '/customer-reminders',
                    name: 'customer-reminders',
                    component: () => import('@/views/CustomerReminderRequest.vue')
                },
                {
                    path: '/customer-satisfaction',
                    name: 'customer-satisfaction',
                    component: () => import('@/views/CustomerSatisfaction.vue')
                },
                {
                    path: '/sentiment-analysis',
                    name: 'sentiment-analysis',
                    component: () => import('@/views/SentimentAnalysis.vue')
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
