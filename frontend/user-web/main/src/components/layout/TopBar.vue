<script setup>
import { useUiStore } from '@/stores/ui'

defineProps({
  title: { type: String, default: '' },
})

const ui = useUiStore()
</script>

<template>
  <header
    class="sticky top-0 z-20 bg-white/90 dark:bg-neutral-900/90 backdrop-blur
           border-b border-gray-100 dark:border-neutral-800"
  >
    <div class="max-w-xl mx-auto relative flex items-center justify-center h-14 px-4">
      <h1 class="text-lg font-bold text-gray-900 dark:text-white">
        {{ title }}
      </h1>

      <button
        class="absolute right-2 p-2 rounded-full text-gray-500 dark:text-gray-300
               hover:bg-gray-100 dark:hover:bg-neutral-800 transition"
        @click="ui.toggle()"
        aria-label="Сменить тему"
      >
        <svg
          v-if="ui.theme === 'light'"
          class="h-6 w-6" fill="none" viewBox="0 0 24 24"
          stroke-width="1.5" stroke="currentColor"
        >
          <path
            stroke-linecap="round" stroke-linejoin="round"
            d="M12 3v2.25m6.364.386-1.591 1.591M21 12h-2.25m-.386 6.364-1.591-1.591M12 18.75V21m-4.773-4.227-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0Z"
          />
        </svg>
        <svg
          v-else
          class="h-6 w-6" fill="none" viewBox="0 0 24 24"
          stroke-width="1.5" stroke="currentColor"
        >
          <path
            stroke-linecap="round" stroke-linejoin="round"
            d="M21.752 15.002A9.72 9.72 0 0 1 18 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 0 0 3 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 0 0 9.002-5.998Z"
          />
        </svg>
      </button>
    </div>
  </header>
</template>
