<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GroupChat from '@/components/learning/GroupChat.vue'

const route = useRoute()
const router = useRouter()
const groupId = computed(() => Number(route.params.groupId))

const back = () => router.push({ name: 'learn' })
</script>

<template>
  <div class="h-screen flex flex-col bg-gray-50 dark:bg-neutral-950">
    <!-- шапка -->
    <header class="shrink-0 sticky top-0 z-10 bg-white/90 dark:bg-neutral-900/90 backdrop-blur
                   border-b border-gray-100 dark:border-neutral-800">
      <div class="max-w-xl mx-auto flex items-center gap-2 h-14 px-3">
        <button class="p-2 -ml-1 rounded-full text-gray-500 hover:bg-gray-100 dark:hover:bg-neutral-800" @click="back">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
          </svg>
        </button>
        <span class="text-lg">💬</span>
        <h1 class="text-sm font-semibold text-gray-900 dark:text-white">Чат группы</h1>
      </div>
    </header>

    <!-- чат на весь экран -->
    <div class="flex-1 min-h-0 max-w-xl w-full mx-auto">
      <GroupChat :group-id="groupId" height="100%" bare />
    </div>
  </div>
</template>
