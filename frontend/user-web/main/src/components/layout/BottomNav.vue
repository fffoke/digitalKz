<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

const items = [
  {
    label: 'AI практика', to: '/practice',
    icon: 'M8.25 7.5l.415-.207a.75.75 0 0 1 1.085.67V10.5m0 0h6m-6 0a48.667 48.667 0 0 0-7.5 0M12 1.5a8.25 8.25 0 0 0-8.25 8.25c0 1.86.61 3.57 1.64 4.95.39.52.6 1.16.6 1.82V19.5a.75.75 0 0 0 .75.75h10.52a.75.75 0 0 0 .75-.75v-2.98c0-.66.21-1.3.6-1.82A8.21 8.21 0 0 0 20.25 9.75 8.25 8.25 0 0 0 12 1.5Z',
  },
  {
    label: 'Обучение', to: '/learn',
    icon: 'M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25',
  },
  {
    label: 'Профиль', to: '/profile',
    icon: 'M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z',
  },
]

// активна, если путь совпадает или вложен (учитывает /learn/:taskId)
const isActive = (to) => route.path === to || route.path.startsWith(to + '/')
</script>

<template>
  <nav
    class="fixed bottom-0 inset-x-0 z-20 bg-white/95 dark:bg-neutral-900/95 backdrop-blur
           border-t border-gray-100 dark:border-neutral-800
           pb-[env(safe-area-inset-bottom)]"
  >
    <div class="max-w-xl mx-auto grid grid-cols-3 px-2 py-1.5">
      <RouterLink
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="flex flex-col items-center gap-1 py-1.5 rounded-2xl transition-colors"
        :class="isActive(item.to) ? 'bg-red-50 dark:bg-neutral-800' : ''"
      >
        <svg
          class="h-6 w-6 transition-colors" fill="none" viewBox="0 0 24 24"
          stroke-width="1.7" stroke="currentColor"
          :class="isActive(item.to) ? 'text-red-500' : 'text-gray-400 dark:text-gray-500'"
        >
          <path stroke-linecap="round" stroke-linejoin="round" :d="item.icon" />
        </svg>

        <span
          class="text-[11px] leading-none transition-colors"
          :class="isActive(item.to)
            ? 'text-red-500 font-semibold'
            : 'text-gray-400 dark:text-gray-500'"
        >
          {{ item.label }}
        </span>
      </RouterLink>
    </div>
  </nav>
</template>
