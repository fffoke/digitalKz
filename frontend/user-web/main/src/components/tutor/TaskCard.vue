<script setup>
// Карточка задания-сценария в списке «AI практика».
const props = defineProps({
  task: { type: Object, required: true },
})
const emit = defineEmits(['open', 'delete'])

const STATUS = {
  new: { label: 'Новое', cls: 'bg-blue-100 text-blue-700' },
  in_progress: { label: 'В процессе', cls: 'bg-amber-100 text-amber-700' },
  done: { label: 'Пройдено', cls: 'bg-green-100 text-green-700' },
}
const DIFF = {
  easy: { label: 'Лёгкое', cls: 'bg-green-50 text-green-600' },
  medium: { label: 'Среднее', cls: 'bg-amber-50 text-amber-600' },
  hard: { label: 'Сложное', cls: 'bg-red-50 text-red-600' },
}

const st = () => STATUS[props.task.status] || STATUS.new
const df = () => DIFF[props.task.difficulty] || DIFF.medium
</script>

<template>
  <div
    class="group w-full bg-white dark:bg-neutral-900 rounded-2xl border
           border-gray-100 dark:border-neutral-800 p-4 hover:border-red-200
           dark:hover:border-neutral-700 transition flex items-start gap-3 cursor-pointer"
    @click="emit('open', task)"
  >
    <div class="h-11 w-11 shrink-0 rounded-xl bg-red-50 dark:bg-neutral-800
                flex items-center justify-center text-xl">
      💬
    </div>

    <div class="flex-1 min-w-0">
      <div class="flex items-center justify-between gap-2">
        <h3 class="font-semibold text-gray-900 dark:text-white text-sm sm:text-base truncate">
          {{ task.title }}
        </h3>
        <div class="flex items-center gap-1.5 shrink-0">
          <span class="px-2 py-0.5 rounded-full text-[11px] font-medium" :class="st().cls">
            {{ st().label }}
          </span>
          <!-- удалить -->
          <button
            type="button"
            class="p-1 rounded-full text-gray-300 hover:text-red-500 hover:bg-red-50
                   dark:hover:bg-neutral-800 transition"
            aria-label="Удалить задание"
            @click.stop="emit('delete', task)"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
            </svg>
          </button>
        </div>
      </div>

      <p v-if="task.description || task.context"
        class="mt-0.5 text-xs sm:text-sm text-gray-500 dark:text-gray-400 line-clamp-2">
        {{ task.description || task.context }}
      </p>

      <div class="mt-2 flex items-center gap-2">
        <span class="px-2 py-0.5 rounded-full text-[11px] font-medium" :class="df().cls">
          {{ df().label }}
        </span>
        <span v-if="task.speaking_score != null"
          class="text-[11px] font-medium text-green-600">
          🎙 SpeakingScore {{ task.speaking_score }}/100
        </span>
      </div>
    </div>
  </div>
</template>
