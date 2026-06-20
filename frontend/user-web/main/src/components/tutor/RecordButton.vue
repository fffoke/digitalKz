<script setup>
import { ref, onBeforeUnmount } from 'vue'

// Одна центральная кнопка записи. Сама управляет MediaRecorder и таймером.
// Тап — старт записи (пульсация + таймер), тап ещё раз — стоп → @recorded(blob, sec).
const props = defineProps({
  disabled: { type: Boolean, default: false }, // пока ИИ думает
})
const emit = defineEmits(['recorded', 'error'])

const recording = ref(false)
const seconds = ref(0)

let mediaRecorder = null
let chunks = []
let stream = null
let timer = null

const fmt = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`

const startTimer = () => {
  seconds.value = 0
  timer = setInterval(() => { seconds.value++ }, 1000)
}
const stopTimer = () => { clearInterval(timer); timer = null }

const start = async () => {
  if (props.disabled) return
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true })
  } catch (e) {
    emit('error', 'Нет доступа к микрофону')
    return
  }
  chunks = []
  mediaRecorder = new MediaRecorder(stream)
  mediaRecorder.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data) }
  mediaRecorder.onstop = () => {
    const blob = new Blob(chunks, { type: 'audio/webm' })
    const sec = seconds.value
    cleanup()
    if (blob.size > 0) emit('recorded', blob, sec)
  }
  mediaRecorder.start()
  recording.value = true
  startTimer()
}

const stop = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop()
}

const cleanup = () => {
  recording.value = false
  stopTimer()
  stream?.getTracks().forEach((t) => t.stop())
  stream = null
  mediaRecorder = null
}

const toggle = () => (recording.value ? stop() : start())

onBeforeUnmount(cleanup)
</script>

<template>
  <div class="flex flex-col items-center gap-2 select-none">
    <button
      type="button"
      :disabled="disabled"
      class="relative h-20 w-20 rounded-full flex items-center justify-center
             transition disabled:opacity-40 disabled:cursor-not-allowed"
      :class="recording
        ? 'bg-red-600'
        : 'bg-red-500 hover:bg-red-600 shadow-lg shadow-red-500/30'"
      @click="toggle"
    >
      <!-- пульсация при записи -->
      <span
        v-if="recording"
        class="absolute inset-0 rounded-full bg-red-500 animate-ping opacity-60"
      />
      <!-- иконка: микрофон / стоп -->
      <svg v-if="!recording" class="relative h-9 w-9 text-white" fill="none"
        viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round"
          d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z" />
      </svg>
      <span v-else class="relative h-7 w-7 rounded-md bg-white" />
    </button>

    <span class="text-xs h-4" :class="recording ? 'text-red-500 font-medium' : 'text-gray-400'">
      {{ recording ? fmt(seconds) + ' · нажмите, чтобы остановить' : 'нажмите и говорите' }}
    </span>
  </div>
</template>
