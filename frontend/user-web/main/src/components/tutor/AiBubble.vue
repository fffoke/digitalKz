<script setup>
// Сообщение ИИ-собеседника (текст). Слева, с аватаркой бота.
defineProps({
  text: { type: String, default: '' },
  typing: { type: Boolean, default: false }, // индикатор «ИИ думает…»
})
</script>

<template>
  <div class="flex justify-start gap-2">
    <div class="h-9 w-9 shrink-0 rounded-full bg-red-100 dark:bg-neutral-800
                flex items-center justify-center text-lg">
      🤖
    </div>

    <div class="max-w-[80%] px-3.5 py-2.5 rounded-2xl rounded-bl-md
                bg-white dark:bg-neutral-800 border border-gray-100 dark:border-neutral-700
                text-gray-800 dark:text-gray-100 text-sm leading-relaxed">
      <template v-if="typing">
        <span class="flex gap-1 py-1">
          <span class="h-2 w-2 rounded-full bg-gray-300 dark:bg-neutral-600 animate-bounce" style="animation-delay:0ms" />
          <span class="h-2 w-2 rounded-full bg-gray-300 dark:bg-neutral-600 animate-bounce" style="animation-delay:150ms" />
          <span class="h-2 w-2 rounded-full bg-gray-300 dark:bg-neutral-600 animate-bounce" style="animation-delay:300ms" />
        </span>
      </template>
      <template v-else>{{ text }}</template>
    </div>
  </div>
</template>
