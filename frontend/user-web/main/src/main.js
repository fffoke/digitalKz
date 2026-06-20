import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router/router';
import { createPinia } from 'pinia';
import { useUserStore } from './stores/user';
import { useUiStore } from './stores/ui';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);

// тема (светлая/тёмная) — применяем до отрисовки
useUiStore().init();

const userStore = useUserStore();
await userStore.fetchUser();

app.use(router);
app.mount('#app')
