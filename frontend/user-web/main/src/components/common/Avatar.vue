<script setup>
defineProps({
  name: { type: String, default: '' },
  src: { type: String, default: '' },
  size: { type: String, default: 'h-11 w-11' },
})
</script>

<template>
  <img
    v-if="src"
    :src="src"
    :class="size"
    class="rounded-full object-cover shrink-0"
    alt=""
  />
  <div
    v-else
    :class="size"
    class="rounded-full bg-gray-200 dark:bg-neutral-700 text-gray-500
           dark:text-gray-300 flex items-center justify-center font-semibold shrink-0"
  >
    {{ (name || '?').charAt(0).toUpperCase() }}
  </div>
</template>
