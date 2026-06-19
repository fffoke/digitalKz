import api from "@/axios/axios";
import { defineStore } from "pinia";

export const useUserStore = defineStore('user', {

    state: () => ({
        user: null,
        token: localStorage.getItem('token') || null,
    }),

    getters: {
        isAuth: (state) => !!state.user,

        isTeacher: (state) => state.user?.role === 'teacher',

        isStudent: (state) => state.user?.role === 'student',
    },

    actions: {

        async fetchUser() {
            try {
                const res = await api.get('/auth/me');

                this.user = res.data;

            } catch (error) {
                console.log(error.response);
            }
        },

        setUser(user) {
            this.user = user;
        }
    }
});