import { defineStore } from 'pinia'

export const useUiStore = defineStore('ui', {
    state: () => ({
        theme: localStorage.getItem('theme') || 'light',
    }),

    actions: {
        apply() {
            document.documentElement.classList.toggle('dark', this.theme === 'dark')
        },

        toggle() {
            this.theme = this.theme === 'dark' ? 'light' : 'dark'
            localStorage.setItem('theme', this.theme)
            this.apply()
        },

        init() {
            this.apply()
        },
    },
})
