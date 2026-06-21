<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import AppLayout from '@/components/layout/AppLayout.vue'
import TaskCard from '@/components/tutor/TaskCard.vue'
import { getInterests, getTasks, generateTasks, createCustomTask, deleteTask, clearCompletedTasks } from '@/services/tutor'

const router = useRouter()
const tasks = ref([])
const loading = ref(true)
const generating = ref(false)
const historyOpen = ref(false)
const clearing = ref(false)
const customOpen = ref(false)
const customSaving = ref(false)
const customError = ref('')
const customForm = ref({
  title: '',
  description: '',
  difficulty: 'medium',
})

const activeTasks = computed(() => tasks.value.filter((t) => t.status !== 'done'))
const completedTasks = computed(() => tasks.value.filter((t) => t.status === 'done'))
const done = computed(() => completedTasks.value.length)
const customValid = computed(() => customForm.value.description.trim().length >= 10)

const load = async () => {
  loading.value = true
  try {
    const { data } = await getInterests()
    if (!data.onboarded) {
      router.replace({ name: 'onboarding-interests' })
      return
    }
    tasks.value = (await getTasks()).data
  } catch (e) {
    console.log(e.response)
  } finally {
    loading.value = false
  }
}

const moreTasks = async () => {
  generating.value = true
  try {
    await generateTasks()
    tasks.value = (await getTasks()).data
  } catch (e) {
    console.log(e.response)
  } finally {
    generating.value = false
  }
}

const openCustomModal = () => {
  customError.value = ''
  customOpen.value = true
}

const closeCustomModal = () => {
  if (customSaving.value) return
  customOpen.value = false
}

const resetCustomForm = () => {
  customForm.value = {
    title: '',
    description: '',
    difficulty: 'medium',
  }
}

const submitCustomTask = async () => {
  if (!customValid.value) return
  customSaving.value = true
  customError.value = ''
  try {
    const payload = {
      title: customForm.value.title.trim() || null,
      description: customForm.value.description.trim(),
      difficulty: customForm.value.difficulty,
    }
    const { data } = await createCustomTask(payload)
    tasks.value = [data, ...tasks.value]
    resetCustomForm()
    customOpen.value = false
  } catch (e) {
    console.log(e.response)
    customError.value = e.response?.data?.detail || 'Не удалось создать сценарий. Попробуйте ещё раз.'
  } finally {
    customSaving.value = false
  }
}

const remove = async (task) => {
  if (!confirm(`Удалить задание «${task.title}»?`)) return
  const prev = tasks.value
  tasks.value = tasks.value.filter((t) => t.id !== task.id)  // оптимистично
  try {
    await deleteTask(task.id)
  } catch (e) {
    console.log(e.response)
    tasks.value = prev  // откат при ошибке
  }
}

const clearCompleted = async () => {
  if (!confirm('Удалить все пройденные задания из истории?')) return
  clearing.value = true
  try {
    await clearCompletedTasks()
    tasks.value = tasks.value.filter((t) => t.status !== 'done')
  } catch (e) {
    console.log(e.response)
  } finally {
    clearing.value = false
  }
}

const open = (task) => router.push({ name: 'conversation', params: { taskId: task.id } })

onMounted(load)
</script>

<template>
  <AppLayout title="AI практика">
    <div class="px-3 sm:px-4 py-4 space-y-4">
      <!-- прогресс -->
      <div v-if="!loading && tasks.length"
        class="bg-gradient-to-br from-red-500 to-red-600 rounded-2xl p-4 text-white">
        <div class="flex items-start justify-between gap-2">
          <div>
            <p class="text-sm opacity-90">Разговорная практика с ИИ</p>
            <p class="text-2xl font-bold mt-0.5">{{ done }} / {{ tasks.length }}</p>
            <p class="text-xs opacity-80 mt-0.5">заданий пройдено</p>
          </div>
          <div class="flex flex-col gap-2">
            <button
              class="shrink-0 flex items-center gap-1.5 bg-white/20 hover:bg-white/30
                    rounded-full px-3 py-1.5 text-xs font-medium transition"
              @click="router.push('/onboarding/interests')"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round"
                  d="M16.862 4.487l1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Z" />
              </svg>
              Интересы
            </button>
            <button
              class="shrink-0 flex items-center justify-center gap-1.5 rounded-full
                     bg-white text-red-600 hover:bg-red-50 px-3 py-1.5
                     text-xs font-semibold shadow-sm transition"
              @click="openCustomModal"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round"
                  d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
              Свой сценарий
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="py-24 text-center text-gray-400">Загрузка…</div>

      <template v-else>
        <!-- активные задания -->
        <div v-if="activeTasks.length" class="space-y-2.5">
          <TaskCard v-for="t in activeTasks" :key="t.id" :task="t" @open="open" @delete="remove" />
        </div>

        <div v-else-if="!completedTasks.length" class="py-16 text-center">
          <div class="text-4xl mb-2">🗒️</div>
          <p class="text-gray-500 dark:text-gray-400 text-sm">Пока нет заданий</p>
          <button
            class="mt-4 inline-flex items-center justify-center gap-1.5 rounded-full
                   bg-red-500 px-4 py-2 text-sm font-semibold text-white
                   hover:bg-red-600 transition"
            @click="openCustomModal"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            Создать свой сценарий
          </button>
        </div>

        <div v-else class="py-10 text-center text-gray-400 text-sm">
          Все задания пройдены 🎉 Сгенерируйте новые ниже.
        </div>

        <button
          class="w-full mt-2 border-2 border-dashed border-gray-200 dark:border-neutral-700
                 text-gray-500 dark:text-gray-400 rounded-2xl py-3 text-sm font-medium
                 hover:border-red-300 hover:text-red-500 transition disabled:opacity-50"
          :disabled="generating"
          @click="moreTasks"
        >
          {{ generating ? 'Генерируем…' : '＋ Сгенерировать ещё задания' }}
        </button>

        <!-- история пройденных (свёрнута, чтобы не мешать) -->
        <div v-if="completedTasks.length" class="pt-2">
          <button
            class="w-full flex items-center justify-between rounded-xl bg-gray-50 dark:bg-neutral-900
                   border border-gray-100 dark:border-neutral-800 px-4 py-2.5 text-sm font-medium
                   text-gray-600 dark:text-gray-300"
            @click="historyOpen = !historyOpen"
          >
            <span>🗂 История пройденных ({{ completedTasks.length }})</span>
            <span class="text-gray-400">{{ historyOpen ? '▲' : '▼' }}</span>
          </button>

          <div v-if="historyOpen" class="mt-2 space-y-2.5">
            <TaskCard v-for="t in completedTasks" :key="t.id" :task="t" @open="open" @delete="remove" />
            <button
              class="w-full rounded-xl bg-gray-100 dark:bg-neutral-800 text-red-500 text-sm font-medium
                     py-2.5 hover:bg-red-50 dark:hover:bg-neutral-700 transition disabled:opacity-50"
              :disabled="clearing"
              @click="clearCompleted"
            >
              {{ clearing ? 'Очищаем…' : 'Удалить все пройденные' }}
            </button>
          </div>
        </div>
      </template>
    </div>

    <Teleport to="body">
      <div
        v-if="customOpen"
        class="fixed inset-0 z-50 flex items-end sm:items-center justify-center
               bg-black/45 px-3 py-4"
        @click.self="closeCustomModal"
      >
        <div
          class="w-full max-w-lg rounded-2xl bg-white dark:bg-neutral-900
                 border border-gray-100 dark:border-neutral-800 p-5 shadow-xl"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <h2 class="text-lg font-bold text-gray-900 dark:text-white">
                Создать свой сценарий
              </h2>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Опишите кейс, который хотите отработать с AI-собеседником.
              </p>
            </div>
            <button
              type="button"
              class="h-9 w-9 shrink-0 rounded-full text-gray-400 hover:bg-gray-100
                     hover:text-gray-700 dark:hover:bg-neutral-800 dark:hover:text-gray-200"
              aria-label="Закрыть"
              @click="closeCustomModal"
            >
              ✕
            </button>
          </div>

          <div class="mt-5 space-y-4">
            <label class="block">
              <span class="text-xs font-semibold text-gray-700 dark:text-gray-200">
                Название <span class="font-normal text-gray-400">(необязательно)</span>
              </span>
              <input
                v-model="customForm.title"
                type="text"
                maxlength="120"
                placeholder="Например: Разговор в поликлинике"
                class="mt-1.5 w-full rounded-xl border border-gray-200 dark:border-neutral-700
                       bg-transparent px-3 py-2.5 text-sm text-gray-800 dark:text-gray-100
                       placeholder:text-gray-400 focus:border-red-400 focus:outline-none"
              >
            </label>

            <label class="block">
              <span class="text-xs font-semibold text-gray-700 dark:text-gray-200">
                Что нужно отработать
              </span>
              <textarea
                v-model="customForm.description"
                rows="5"
                maxlength="1200"
                placeholder="Например: я пришёл в поликлинику, хочу объяснить врачу симптомы, спросить про анализы и уточнить время следующего приёма."
                class="mt-1.5 w-full rounded-xl border border-gray-200 dark:border-neutral-700
                       bg-transparent px-3 py-2.5 text-sm text-gray-800 dark:text-gray-100
                       placeholder:text-gray-400 focus:border-red-400 focus:outline-none resize-none"
              />
              <span class="mt-1 block text-xs text-gray-400">
                Лучше писать: место, роль собеседника, цель разговора и 2-3 детали.
              </span>
            </label>

            <div>
              <p class="text-xs font-semibold text-gray-700 dark:text-gray-200">Сложность</p>
              <div class="mt-1.5 grid grid-cols-3 gap-2">
                <button
                  v-for="level in [
                    { key: 'easy', label: 'Легко' },
                    { key: 'medium', label: 'Средне' },
                    { key: 'hard', label: 'Сложно' },
                  ]"
                  :key="level.key"
                  type="button"
                  class="rounded-xl border px-3 py-2 text-sm transition"
                  :class="customForm.difficulty === level.key
                    ? 'border-red-500 bg-red-50 text-red-600 dark:bg-neutral-800'
                    : 'border-gray-200 text-gray-500 dark:border-neutral-700 dark:text-gray-300'"
                  @click="customForm.difficulty = level.key"
                >
                  {{ level.label }}
                </button>
              </div>
            </div>

            <p v-if="customError" class="text-sm text-red-500">{{ customError }}</p>

            <div class="flex gap-2 pt-1">
              <button
                type="button"
                class="flex-1 rounded-xl border border-gray-200 py-3 text-sm font-semibold
                       text-gray-600 hover:bg-gray-50 dark:border-neutral-700
                       dark:text-gray-300 dark:hover:bg-neutral-800"
                @click="closeCustomModal"
              >
                Отмена
              </button>
              <button
                type="button"
                class="flex-1 rounded-xl bg-red-500 py-3 text-sm font-semibold
                       text-white hover:bg-red-600 disabled:opacity-40"
                :disabled="!customValid || customSaving"
                @click="submitCustomTask"
              >
                {{ customSaving ? 'Создаём…' : 'Создать' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </AppLayout>
</template>
