import { useUserStore } from "@/stores/user";
import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', name: 'landing', component: () => import('@/pages/landing.vue'), meta: { guestOnly: true } },
        { path: '/login', name: 'login', component: () => import('@/pages/auth/login.vue'), meta: { guestOnly: true } },
        { path: '/register', name: 'register', component: () => import('@/pages/auth/register.vue'), meta: { guestOnly: true } },
        { path: '/verify', name: 'verify', component: () => import('@/pages/auth/verify.vue'), meta: { authOnly: true } },
        { path: '/verify-pending', name: 'verify-pending', component: () => import('@/pages/auth/verify-pending.vue'), meta: { authOnly: true } },
        { path: '/home', name: 'home', component: () => import('@/pages/home.vue'), meta: { authOnly: true } },
    ]
});

router.beforeEach((to, from, next) => {
    const userStore = useUserStore();

    if(to.meta.guestOnly && userStore.isAuth){
        next({ name: 'landing' });
    }

    if(to.meta.authOnly && !userStore.isAuth){
        next({ name: 'login' });
    }
    
    next();
});

export default router;