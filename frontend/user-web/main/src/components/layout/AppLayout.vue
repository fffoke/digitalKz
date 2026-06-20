<script setup>
import TopBar from '@/components/layout/TopBar.vue'
import BottomNav from '@/components/layout/BottomNav.vue'

defineProps({
  title: { type: String, default: '' },
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50 dark:bg-neutral-950">
    <TopBar :title="title" />

    <main class="flex-1 w-full max-w-xl mx-auto pb-24">
      <slot />
    </main>

    <BottomNav />
  </div>
</template>
