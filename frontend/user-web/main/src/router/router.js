import { useUserStore } from "@/stores/user";
import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
    history: createWebHistory(),
    routes: [
        // гостевые
        { path: '/', name: 'landing', component: () => import('@/pages/landing.vue'), meta: { guestOnly: true } },
        { path: '/login', name: 'login', component: () => import('@/pages/auth/login.vue'), meta: { guestOnly: true } },
        { path: '/register', name: 'register', component: () => import('@/pages/auth/register.vue'), meta: { guestOnly: true } },

        // онбординг интересов AI-практики (первый вход)
        { path: '/onboarding/interests', name: 'onboarding-interests', component: () => import('@/pages/onboarding/interests.vue'), meta: { authOnly: true } },

        // AI практика (новая идея)
        { path: '/practice', name: 'practice', component: () => import('@/pages/practice/practice.vue'), meta: { authOnly: true } },
        { path: '/practice/:taskId', name: 'conversation', component: () => import('@/pages/practice/conversation.vue'), meta: { authOnly: true } },

        // Обучение (старая идея: роли преподаватель/ученик, группы)
        { path: '/learn', name: 'learn', component: () => import('@/pages/learn/learn.vue'), meta: { authOnly: true } },

        { path: '/profile', name: 'profile', component: () => import('@/pages/profile/profile.vue'), meta: { authOnly: true } },
        { path: '/profile/edit', name: 'profile-edit', component: () => import('@/pages/profile/edit-profile.vue'), meta: { authOnly: true } },
    ]
});

router.beforeEach((to) => {
    const userStore = useUserStore();

    if (to.meta.guestOnly && userStore.isAuth) {
        return { name: 'practice' };
    }

    if (to.meta.authOnly && !userStore.isAuth) {
        return { name: 'login' };
    }
});

export default router;
