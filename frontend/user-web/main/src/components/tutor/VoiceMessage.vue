<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'

// Голосовой баббл «как в Telegram»: play/pause + волна + длительность.
// Можно переслушать себя. src — blob URL (локально) или URL с бэка.
const props = defineProps({
  src: { type: String, required: true },
  duration: { type: Number, default: 0 },   // секунды (известны при записи)
  mine: { type: Boolean, default: true },
  transcript: { type: String, default: '' },
  pending: { type: Boolean, default: false },
  failed: { type: Boolean, default: false },
})

const audio = new Audio(props.src)
const playing = ref(false)
const progress = ref(0)   // 0..1
const total = ref(props.duration || 0)

audio.addEventListener('loadedmetadata', () => {
  if (isFinite(audio.duration)) total.value = audio.duration
})
audio.addEventListener('timeupdate', () => {
  if (total.value) progress.value = audio.currentTime / total.value
})
audio.addEventListener('ended', () => {
  playing.value = false
  progress.value = 0
})

const toggle = () => {
  if (playing.value) { audio.pause(); playing.value = false }
  else { audio.play(); playing.value = true }
}

// показывать ли текст расшифровки — управляется флагом в .env
const showTranscript = import.meta.env.VITE_SHOW_TRANSCRIPT === 'true'

// статичная «волна» — детерминированные столбики
const bars = Array.from({ length: 28 }, (_, i) => 30 + ((i * 37) % 70))
const activeBar = computed(() => Math.round(progress.value * bars.length))

const fmt = (s) => {
  s = Math.round(s || 0)
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}

onBeforeUnmount(() => { audio.pause() })
</script>

<template>
  <div class="flex" :class="mine ? 'justify-end' : 'justify-start'">
    <div class="max-w-[80%] space-y-1">
      <div
        class="flex items-center gap-3 px-3 py-2 rounded-2xl"
        :class="mine
          ? 'bg-red-500 text-white rounded-br-md'
          : 'bg-white dark:bg-neutral-800 text-gray-800 dark:text-gray-100 rounded-bl-md border border-gray-100 dark:border-neutral-700'"
      >
        <button
          type="button"
          class="h-9 w-9 shrink-0 rounded-full flex items-center justify-center"
          :class="mine ? 'bg-white/20' : 'bg-red-500 text-white'"
          @click="toggle"
        >
          <svg v-if="!playing" class="h-5 w-5" :class="mine ? 'text-white' : 'text-white'"
            viewBox="0 0 24 24" fill="currentColor">
            <path d="M8 5v14l11-7z" />
          </svg>
          <svg v-else class="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
            <path d="M6 5h4v14H6zM14 5h4v14h-4z" />
          </svg>
        </button>

        <!-- волна -->
        <div class="flex items-center gap-[2px] h-7">
          <span
            v-for="(h, i) in bars" :key="i"
            class="w-[2px] rounded-full transition-colors"
            :class="[
              mine ? (i < activeBar ? 'bg-white' : 'bg-white/40')
                   : (i < activeBar ? 'bg-red-500' : 'bg-gray-300 dark:bg-neutral-600')
            ]"
            :style="{ height: h + '%' }"
          />
        </div>

        <span class="text-xs tabular-nums shrink-0"
          :class="mine ? 'text-white/80' : 'text-gray-400'">
          {{ fmt(total) }}
        </span>
      </div>

      <!-- статус / расшифровка (видимость текста — по флагу VITE_SHOW_TRANSCRIPT) -->
      <p v-if="pending" class="text-xs text-gray-400 text-right pr-1">отправка…</p>
      <p v-else-if="failed" class="text-xs text-red-400 text-right pr-1">не отправилось</p>
      <p v-else-if="showTranscript && transcript"
        class="text-xs text-gray-500 dark:text-gray-400"
        :class="mine ? 'text-right pr-1' : 'pl-1'">
        «{{ transcript }}»
      </p>
    </div>
  </div>
</template>
