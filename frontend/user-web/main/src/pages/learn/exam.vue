<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import RecordButton from '@/components/tutor/RecordButton.vue'
import { getLevelExam, submitLevelExam } from '@/services/learning'

const router = useRouter()
const exam = ref(null)
const loading = ref(true)
const submitting = ref(false)
const result = ref(null)
const error = ref('')

const answers = ref({})        // q{idx} -> ответ
const speakBlob = ref(null)
const recorded = ref(false)

onMounted(async () => {
  try {
    exam.value = (await getLevelExam()).data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось загрузить экзамен'
  } finally {
    loading.value = false
  }
})

const onRecorded = (blob) => {
  speakBlob.value = blob
  recorded.value = true
}

const submit = async () => {
  submitting.value = true
  error.value = ''
  try {
    result.value = (await submitLevelExam(answers.value, speakBlob.value)).data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось сдать экзамен'
  } finally {
    submitting.value = false
  }
}

const fmtDate = (iso) => new Date(iso).toLocaleDateString('ru')
const back = () => router.push({ name: 'learn' })
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-neutral-950">
    <!-- шапка -->
    <header class="sticky top-0 z-10 bg-white/90 dark:bg-neutral-900/90 backdrop-blur border-b border-gray-100 dark:border-neutral-800">
      <div class="max-w-xl mx-auto flex items-center gap-2 h-14 px-3">
        <button class="p-2 -ml-1 rounded-full text-gray-500 hover:bg-gray-100 dark:hover:bg-neutral-800" @click="back">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
          </svg>
        </button>
        <h1 class="text-sm font-semibold text-gray-900 dark:text-white">
          Экзамен на повышение<span v-if="exam?.target_level"> → {{ exam.target_level }}</span>
        </h1>
      </div>
    </header>

    <div class="max-w-xl mx-auto px-3 sm:px-4 py-4">
      <div v-if="loading" class="py-24 text-center text-gray-400">Загрузка…</div>

      <!-- результат -->
      <div v-else-if="result" class="bg-white dark:bg-neutral-900 rounded-2xl border border-gray-100 dark:border-neutral-800 p-6 text-center space-y-3">
        <div class="text-4xl">{{ result.score >= 70 ? '🎉' : '📚' }}</div>
        <div class="text-3xl font-bold" :class="result.score >= 70 ? 'text-green-600' : 'text-amber-600'">{{ result.score }}%</div>
        <p class="text-sm text-gray-700 dark:text-gray-200">{{ result.verdict }}</p>
        <button class="w-full bg-gray-800 hover:bg-gray-700 text-white font-semibold rounded-xl py-3 text-sm" @click="back">
          К обучению
        </button>
      </div>

      <!-- недоступно (лимит 2 недели) -->
      <div v-else-if="exam && !exam.can_take" class="bg-amber-50 dark:bg-neutral-900 rounded-2xl border border-amber-200 dark:border-neutral-800 p-6 text-center">
        <div class="text-3xl">⏳</div>
        <h2 class="mt-2 font-bold text-gray-900 dark:text-white">Экзамен пока недоступен</h2>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Досрочно экзамен можно сдавать раз в 2 недели.
          <template v-if="exam.next_available_at"><br>Следующая попытка: {{ fmtDate(exam.next_available_at) }}</template>
        </p>
        <button class="mt-4 w-full bg-gray-100 dark:bg-neutral-800 rounded-xl py-2.5 text-sm font-medium" @click="back">Назад</button>
      </div>

      <!-- экзамен -->
      <div v-else-if="exam" class="space-y-4">
        <p v-if="!exam.configured" class="text-sm text-gray-400 bg-white dark:bg-neutral-900 rounded-xl border border-gray-100 dark:border-neutral-800 p-3">
          Тестовые вопросы для этого уровня ещё не добавлены администратором — сдайте голосовую часть.
        </p>

        <!-- вопросы -->
        <div v-for="(q, idx) in exam.questions" :key="idx"
             class="bg-white dark:bg-neutral-900 rounded-2xl border border-gray-100 dark:border-neutral-800 p-4">
          <p class="text-sm font-medium text-gray-800 dark:text-gray-100">{{ idx + 1 }}. {{ q.text }}</p>

          <!-- аудирование: послушать и написать -->
          <div v-if="q.type === 'listening'" class="mt-2 space-y-2">
            <audio v-if="q.audio_url" :src="q.audio_url" controls class="w-full h-9" />
            <input v-model="answers[`q${idx}`]" placeholder="Напишите, что услышали"
              class="w-full rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800 text-gray-900 dark:text-white px-3 py-2.5 text-sm focus:border-red-400 focus:outline-none" />
          </div>

          <!-- выбор варианта -->
          <div v-else class="mt-2 flex flex-wrap gap-2">
            <button v-for="opt in q.options" :key="opt"
              class="rounded-lg border px-3 py-2 text-sm transition"
              :class="answers[`q${idx}`] === opt ? 'border-red-500 bg-red-50 text-red-600' : 'border-gray-200 text-gray-600 dark:border-neutral-700 dark:text-gray-300'"
              @click="answers[`q${idx}`] = opt">
              {{ opt }}
            </button>
          </div>
        </div>

        <!-- голосовое задание -->
        <div class="bg-white dark:bg-neutral-900 rounded-2xl border border-gray-100 dark:border-neutral-800 p-5">
          <h3 class="font-semibold text-gray-900 dark:text-white text-sm">🎙 Голосовое задание</h3>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ exam.voice_task }}</p>
          <div class="mt-4 flex flex-col items-center gap-2">
            <RecordButton :disabled="submitting" @recorded="onRecorded" />
            <p v-if="recorded" class="text-xs text-green-600">Голос записан ✓ (можно перезаписать)</p>
          </div>
        </div>

        <p v-if="error" class="text-sm text-red-500 text-center">{{ error }}</p>

        <button
          class="w-full bg-red-500 hover:bg-red-600 disabled:opacity-50 text-white font-semibold rounded-xl py-3.5 text-sm transition"
          :disabled="submitting" @click="submit">
          {{ submitting ? 'Проверяем…' : 'Сдать экзамен' }}
        </button>
      </div>

      <p v-else class="py-24 text-center text-red-400">{{ error }}</p>
    </div>
  </div>
</template>
