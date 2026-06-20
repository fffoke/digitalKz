<script setup>
import { reactive } from 'vue'

import AuthLayout from '@/components/AuthLayout.vue'
import AuthInput from '@/components/AuthInput.vue'
import AuthButton from '@/components/AuthButton.vue'

import { register } from '@/services/auth'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const router = useRouter()

const userStore = useUserStore()

const form = reactive({
  name: '',
  email: '',
  password: ''
})

const errors = reactive({
  name: '',
  email: '',
  password: '',
  general: ''
})

const loading = reactive({
  value: false
})

const validate = () => {

  errors.name = ''
  errors.email = ''
  errors.password = ''
  errors.general = ''

  let isValid = true

  if (!form.name.trim()) {
    errors.name = 'Введите имя'
    isValid = false
  }

  if (!form.email.trim()) {
    errors.email = 'Введите email'
    isValid = false
  }

  else if (!/\S+@\S+\.\S+/.test(form.email)) {
    errors.email = 'Некорректный email'
    isValid = false
  }

  if (!form.password.trim()) {
    errors.password = 'Введите пароль'
    isValid = false
  }

  else if (form.password.length < 8) {
    errors.password = 'Минимум 8 символов'
    isValid = false
  }

  return isValid
}

const regFunc = async () => {

  if (!validate()) return

  try {
    loading.value = true

    const res = await register(form)

    localStorage.setItem('token', res.data.access_token)

    await userStore.fetchUser()

    // первый вход → онбординг интересов разрулит вкладка «AI практика»
    router.push({ name: 'practice' })

  } catch (error) {

    console.log(error.response)

    if (error.response?.data?.detail) {
      errors.general = error.response.data.detail
    }

  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLayout
    title="Создать аккаунт"
    subtitle="Бесплатное изучение казахского языка"
  >
    <form
      class="space-y-8"
      @submit.prevent="regFunc"
    >
      <AuthInput
        v-model="form.name"
        label="Имя"
        placeholder="Айдар"
        :error="errors.name"
      />

      <AuthInput
        v-model="form.email"
        label="Email"
        placeholder="name@example.kz"
        :error="errors.email"
      />

      <AuthInput
        v-model="form.password"
        label="Пароль"
        type="password"
        placeholder="Минимум 8 символов"
        :error="errors.password"
      />

      <p
        v-if="errors.general"
        class="text-red-500 text-center"
      >
        {{ errors.general }}
      </p>

      <AuthButton
        :disabled="loading.value"
      >
        {{ loading.value ? 'Создание...' : 'Создать аккаунт' }}
      </AuthButton>
    </form>

    <p class="text-center text-gray-500 mt-10">
      Регистрируясь, вы принимаете условия использования платформы
    </p>

    <p class="text-center text-xl md:text-2xl mt-12">
      Уже есть аккаунт?

      <RouterLink
        to="/login"
        class="text-red-500 font-semibold"
      >
        Войти
      </RouterLink>
    </p>
  </AuthLayout>
</template>
