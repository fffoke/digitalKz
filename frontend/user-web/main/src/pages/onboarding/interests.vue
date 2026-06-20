<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import InterestForm from '@/components/tutor/InterestForm.vue'
import { getInterests, saveInterests, generateTasks } from '@/services/tutor'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const initial = ref(null)
const editing = ref(false)
const ready = ref(false)

onMounted(async () => {
  try {
    const { data } = await getInterests()
    if (data.onboarded) {
      editing.value = true
      initial.value = data       // предзаполняем для редактирования
    }
  } catch (e) {
    console.log(e.response)
  } finally {
    ready.value = true
  }
})

const onSubmit = async (data) => {
  loading.value = true
  error.value = ''
  try {
    await saveInterests(data)
    await generateTasks()          // пересоздаём задания под новые ответы
    router.replace({ name: 'practice' })
  } catch (e) {
    console.log(e.response)
    error.value = 'Не удалось сохранить. Попробуйте ещё раз.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-neutral-950">
    <div class="max-w-xl mx-auto px-4 sm:px-6 py-8">
      <div class="text-center mb-8">
        <div class="text-4xl mb-2">{{ editing ? '✏️' : '👋' }}</div>
        <h1 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
          {{ editing ? 'Изменить интересы' : 'Давай познакомимся' }}
        </h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {{ editing
            ? 'Обновите ответы — задания пересоберутся под них'
            : 'Ответьте на вопросы — подберём задания под вас' }}
        </p>
      </div>

      <div v-if="ready" class="bg-white dark:bg-neutral-900 rounded-2xl border
                  border-gray-100 dark:border-neutral-800 p-5 sm:p-6">
        <InterestForm
          :loading="loading"
          :initial="initial"
          :submit-label="editing ? 'Сохранить и пересоздать' : 'Создать задания'"
          @submit="onSubmit"
        />
        <p v-if="error" class="mt-3 text-sm text-red-500 text-center">{{ error }}</p>
      </div>
    </div>
  </div>
</template>
