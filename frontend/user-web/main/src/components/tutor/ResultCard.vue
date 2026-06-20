<script setup>
// Экран результата после завершения сессии.
// language_score = SpeakingScore (качество речи), task_score = выполнение задания.
const props = defineProps({
  result: { type: Object, required: true }, // { task_score, language_score, feedback }
})
defineEmits(['close'])

const ring = (v) =>
  v >= 75 ? 'text-green-500' : v >= 50 ? 'text-amber-500' : 'text-red-500'
const bar = (v) =>
  v >= 75 ? 'bg-green-500' : v >= 50 ? 'bg-amber-500' : 'bg-red-500'

// длина окружности для прогресс-кольца (r=52)
const C = 2 * Math.PI * 52
</script>

<template>
  <div class="space-y-5">
    <div class="text-center">
      <div class="text-3xl">🎉</div>
      <h2 class="mt-1 text-lg font-bold text-gray-900 dark:text-white">Задание завершено</h2>
    </div>

    <!-- SpeakingScore — кольцо -->
    <div class="flex flex-col items-center">
      <div class="relative h-32 w-32">
        <svg class="h-32 w-32 -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="52" fill="none" stroke-width="10"
            class="text-gray-100 dark:text-neutral-800" stroke="currentColor" />
          <circle cx="60" cy="60" r="52" fill="none" stroke-width="10"
            stroke-linecap="round" :class="ring(result.language_score)" stroke="currentColor"
            :stroke-dasharray="C"
            :stroke-dashoffset="C - (C * result.language_score) / 100" />
        </svg>
        <div class="absolute inset-0 flex flex-col items-center justify-center">
          <span class="text-3xl font-bold text-gray-900 dark:text-white">
            {{ result.language_score }}
          </span>
          <span class="text-[11px] text-gray-400">из 100</span>
        </div>
      </div>
      <p class="mt-2 text-sm font-semibold text-gray-900 dark:text-white">SpeakingScore</p>
      <p class="text-xs text-gray-400">качество казахской речи</p>
    </div>

    <!-- выполнение задания -->
    <div>
      <div class="flex justify-between text-sm mb-1">
        <span class="text-gray-600 dark:text-gray-300">Выполнение задания</span>
        <span class="font-semibold text-gray-900 dark:text-white">{{ result.task_score }}%</span>
      </div>
      <div class="h-2.5 rounded-full bg-gray-100 dark:bg-neutral-800 overflow-hidden">
        <div class="h-full rounded-full transition-all" :class="bar(result.task_score)"
          :style="{ width: result.task_score + '%' }" />
      </div>
    </div>

    <!-- разбор -->
    <div v-if="result.feedback"
      class="bg-gray-50 dark:bg-neutral-800 rounded-xl p-3.5 text-sm
             text-gray-700 dark:text-gray-200 leading-relaxed whitespace-pre-line">
      {{ result.feedback }}
    </div>

    <button
      class="w-full bg-gray-800 hover:bg-gray-700 text-white font-semibold rounded-xl py-3 text-sm transition"
      @click="$emit('close')"
    >
      К заданиям
    </button>
  </div>
</template>
