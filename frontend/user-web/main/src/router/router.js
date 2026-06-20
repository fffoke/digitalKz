import { useUserStore } from "@/stores/user";
import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
    history: createWebHistory(),
    routes: [
        // гостевые
        { path: '/', name: 'landing', component: () => import('@/pages/landing.vue'), meta: { guestOnly: true } },
        { path: '/login', name: 'login', component: () => import('@/pages/auth/login.vue'), meta: { guestOnly: true } },
        { path: '/register', name: 'register', component: () => import('@/pages/auth/register.vue'), meta: { guestOnly: true } },

        // онбординг роли
        { path: '/verify', name: 'verify', component: () => import('@/pages/auth/verify.vue'), meta: { authOnly: true } },
        { path: '/verify-pending', name: 'verify-pending', component: () => import('@/pages/auth/verify-pending.vue'), meta: { authOnly: true } },

        // основные вкладки
        { path: '/home', name: 'home', component: () => import('@/pages/feed/home.vue'), meta: { authOnly: true } },
        { path: '/messages', name: 'messages', component: () => import('@/pages/messages/messages.vue'), meta: { authOnly: true } },
        { path: '/learn', name: 'learn', component: () => import('@/pages/learn/learn.vue'), meta: { authOnly: true } },
        { path: '/activity', name: 'activity', component: () => import('@/pages/activity/activity.vue'), meta: { authOnly: true } },
        { path: '/profile', name: 'profile', component: () => import('@/pages/profile/profile.vue'), meta: { authOnly: true } },
    ]
});

router.beforeEach((to) => {
    const userStore = useUserStore();

    if (to.meta.guestOnly && userStore.isAuth) {
        return { name: 'home' };
    }

    if (to.meta.authOnly && !userStore.isAuth) {
        return { name: 'login' };
    }
});

export default router;
