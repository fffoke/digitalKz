<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'

import AuthLayout from '@/components/AuthLayout.vue'
import AuthInput from '@/components/AuthInput.vue'
import AuthButton from '@/components/AuthButton.vue'

import api from '@/axios/axios'

const router = useRouter();

const form = reactive({
  iin: '',
  doc_photo: null
})

const loading = reactive({
  value: false
})

const handleFile = (event) => {
  form.doc_photo = event.target.files[0]
}

const submitVerification = async () => {
  try {
    loading.value = true

    const formData = new FormData()

    formData.append('iin', form.iin)
    formData.append('doc_photo', form.doc_photo)

    await api.post('/verification', formData)

    router.push('/');

  } catch (error) {
    console.log(error.response)

  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLayout
    title="Верификация личности"
    subtitle="Подтвердите личность для доступа ко всем возможностям платформы"
  >
    <form
      class="space-y-8"
      @submit.prevent="submitVerification"
    >
      <AuthInput
        v-model="form.iin"
        label="ИИН"
        placeholder="000000000000"
      />

      <div>
        <label
          class="block mb-3 text-xl md:text-2xl font-medium"
        >
          Фото удостоверения
        </label>

        <label
          class="flex flex-col items-center justify-center
                 w-full min-h-[180px]
                 rounded-3xl border-2 border-dashed border-gray-300
                 bg-white cursor-pointer
                 hover:border-red-400 transition"
        >
          <input
            type="file"
            class="hidden"
            accept="image/*"
            @change="handleFile"
          />

          <div
            class="text-center px-4"
          >
            <p
              class="text-lg md:text-xl font-medium"
            >
              Загрузить документ
            </p>

            <p
              class="mt-2 text-gray-500 text-sm md:text-base"
            >
              JPG, PNG или HEIC
            </p>

            <p
              v-if="form.doc_photo"
              class="mt-4 text-red-500 font-medium"
            >
              {{ form.doc_photo.name }}
            </p>
          </div>
        </label>
      </div>

      <AuthButton
        :disabled="loading.value"
      >
        {{ loading.value ? 'Отправка...' : 'Отправить на проверку' }}
      </AuthButton>
    </form>

    <p
      class="text-center text-gray-500 mt-10 text-sm md:text-base"
    >
      Обычно проверка занимает 5–15 минут
    </p>
  </AuthLayout>
</template>