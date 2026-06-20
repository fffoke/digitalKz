<script setup>
import AppLayout from '@/components/layout/AppLayout.vue'

defineProps({
  title: { type: String, default: '' },
})
</script>

<template>
  <AppLayout :title="title">
    <div class="flex flex-col items-center justify-center text-center px-6 py-24 gap-3">
      <div class="h-16 w-16 rounded-2xl bg-red-50 dark:bg-neutral-800
                  flex items-center justify-center">
        <svg class="h-8 w-8 text-red-400" fill="none" viewBox="0 0 24 24"
          stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round"
            d="M11.25 11.25l.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
        </svg>
      </div>
      <p class="text-lg font-semibold text-gray-700 dark:text-gray-200">{{ title }}</p>
      <p class="text-sm text-gray-400">Этот раздел скоро появится</p>
    </div>
  </AppLayout>
</template>
