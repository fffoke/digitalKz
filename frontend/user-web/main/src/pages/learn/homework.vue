<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getHomeworks, submitHomework, gradeHomework } from '@/services/learning'

const router = useRouter()
const user = useUserStore()
const isTeacher = ref(user.user?.role === 'teacher')

const items = ref([])
const loading = ref(true)
const busy = ref(null)        // id, по которому идёт действие

// драфты ученика и преподавателя
const drafts = ref({})        // hwId -> { text, file }
const grades = ref({})        // hwId -> { grade, feedback }

const STATUS = {
  assigned: { label: 'Нужно сдать', cls: 'bg-amber-100 text-amber-700' },
  submitted: { label: 'На проверке', cls: 'bg-blue-100 text-blue-700' },
  graded: { label: 'Проверено', cls: 'bg-green-100 text-green-700' },
}

const load = async () => {
  loading.value = true
  try {
    items.value = (await getHomeworks()).data
  } catch (e) {
    console.log(e.response)
  } finally {
    loading.value = false
  }
}
onMounted(load)

const draft = (id) => (drafts.value[id] ||= { text: '', file: null })
const onFile = (id, e) => { draft(id).file = e.target.files[0] || null }

const send = async (hw) => {
  const d = draft(hw.id)
  if (!d.text.trim() && !d.file) return
  busy.value = hw.id
  try {
    await submitHomework(hw.id, d.text, d.file)
    await load()
  } catch (e) {
    alert(e.response?.data?.detail || 'Не удалось сдать')
  } finally {
    busy.value = null
  }
}

const gradeDraft = (id) => (grades.value[id] ||= { grade: 90, feedback: '' })
const grade = async (hw) => {
  const g = gradeDraft(hw.id)
  busy.value = hw.id
  try {
    await gradeHomework(hw.id, { grade: Number(g.grade), feedback: g.feedback })
    await load()
  } catch (e) {
    alert(e.response?.data?.detail || 'Не удалось оценить')
  } finally {
    busy.value = null
  }
}

const back = () => router.push({ name: 'learn' })
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-neutral-950">
    <header class="sticky top-0 z-10 bg-white/90 dark:bg-neutral-900/90 backdrop-blur border-b border-gray-100 dark:border-neutral-800">
      <div class="max-w-xl mx-auto flex items-center gap-2 h-14 px-3">
        <button class="p-2 -ml-1 rounded-full text-gray-500 hover:bg-gray-100 dark:hover:bg-neutral-800" @click="back">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
          </svg>
        </button>
        <h1 class="text-sm font-semibold text-gray-900 dark:text-white">
          {{ isTeacher ? 'Проверка ДЗ' : 'Мои домашние задания' }}
        </h1>
      </div>
    </header>

    <div class="max-w-xl mx-auto px-3 sm:px-4 py-4 space-y-3">
      <div v-if="loading" class="py-24 text-center text-gray-400">Загрузка…</div>
      <div v-else-if="!items.length" class="py-20 text-center text-gray-400 text-sm">Заданий пока нет</div>

      <div v-for="hw in items" :key="hw.id"
           class="bg-white dark:bg-neutral-900 rounded-2xl border border-gray-100 dark:border-neutral-800 p-4">
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0">
            <p v-if="isTeacher" class="text-xs text-gray-400">{{ hw.group_name }} · {{ hw.student_name }}</p>
            <p class="text-sm font-medium text-gray-800 dark:text-gray-100 mt-0.5">{{ hw.task }}</p>
          </div>
          <span class="shrink-0 px-2 py-0.5 rounded-full text-[11px] font-medium" :class="STATUS[hw.status]?.cls">
            {{ STATUS[hw.status]?.label }}
          </span>
        </div>

        <!-- сдача (ученик) -->
        <template v-if="!isTeacher && hw.status === 'assigned'">
          <textarea v-model="draft(hw.id).text" rows="2" placeholder="Ответ текстом (необязательно)"
            class="mt-3 w-full rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800 text-gray-900 dark:text-white px-3 py-2.5 text-sm focus:border-red-400 focus:outline-none resize-none" />
          <label class="mt-2 block text-xs text-gray-500">Фото тетради / файл</label>
          <input type="file" accept="image/*" @change="(e) => onFile(hw.id, e)"
            class="mt-1 block w-full text-sm text-gray-500 file:mr-3 file:rounded-lg file:border-0 file:bg-gray-100 dark:file:bg-neutral-800 file:px-3 file:py-2 file:text-sm file:font-medium file:text-gray-700 dark:file:text-gray-200" />
          <button class="mt-3 w-full rounded-xl bg-red-500 hover:bg-red-600 disabled:opacity-50 py-2.5 text-sm font-semibold text-white"
                  :disabled="busy === hw.id" @click="send(hw)">
            {{ busy === hw.id ? 'Отправка…' : 'Сдать ДЗ' }}
          </button>
        </template>

        <!-- отправленное / проверенное (видят оба) -->
        <template v-else>
          <div v-if="hw.submission || hw.submission_file" class="mt-3 rounded-xl bg-gray-50 dark:bg-neutral-800 p-3 space-y-2">
            <p v-if="hw.submission" class="text-sm text-gray-700 dark:text-gray-200 whitespace-pre-line">{{ hw.submission }}</p>
            <a v-if="hw.submission_file" :href="hw.submission_file" target="_blank" class="block">
              <img :src="hw.submission_file" alt="ДЗ" class="max-h-56 rounded-lg border border-gray-100 dark:border-neutral-700" />
            </a>
          </div>

          <!-- оценка (преподаватель) -->
          <template v-if="isTeacher && hw.status === 'submitted'">
            <div class="mt-3 flex items-end gap-2">
              <div>
                <label class="block text-xs text-gray-500 mb-1">Балл</label>
                <input v-model="gradeDraft(hw.id).grade" type="number" min="1" max="100"
                  class="w-20 rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800 text-gray-900 dark:text-white px-3 py-2 text-sm" />
              </div>
              <input v-model="gradeDraft(hw.id).feedback" placeholder="Комментарий"
                class="flex-1 rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800 text-gray-900 dark:text-white px-3 py-2 text-sm" />
              <button class="rounded-xl bg-green-500 hover:bg-green-600 disabled:opacity-50 px-4 py-2 text-sm font-semibold text-white"
                      :disabled="busy === hw.id" @click="grade(hw)">Оценить</button>
            </div>
          </template>

          <!-- итог -->
          <div v-if="hw.status === 'graded'" class="mt-3 flex items-center gap-2 text-sm">
            <span class="font-semibold text-green-600">Оценка: {{ hw.grade }}/100</span>
            <span v-if="hw.feedback" class="text-gray-500">— {{ hw.feedback }}</span>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
