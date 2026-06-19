```vue
<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import AuthLayout from '@/components/AuthLayout.vue'
import AuthInput from '@/components/AuthInput.vue'
import AuthButton from '@/components/AuthButton.vue'

import { login } from '@/services/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const remember = ref(false)

const form = reactive({
    email: '',
    password: ''
})

const errors = reactive({
    email: '',
    password: '',
    general: ''
})

const loading = ref(false)

const validate = () => {
    errors.email = ''
    errors.password = ''
    errors.general = ''

    let isValid = true

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
        errors.password = 'Пароль слишком короткий'
        isValid = false
    }

    return isValid
}

const loginFunc = async () => {
    if (!validate()) return

    try {
        loading.value = true

        const res = await login(form)

        localStorage.setItem('token', res.data.access_token)

        await userStore.fetchUser()

        const user = userStore.user

        if (user.verification_status === 'pending') {
            router.push({ name: 'verify-pending' })
            return
        }

        if (user.verification_status === 'rejected') {
            router.push({ name: 'verify' })
            return
        }

        router.push({ name: 'home' })

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
    title="С возвращением"
    subtitle="Войдите, чтобы продолжить обучение"
  >
    <form class="space-y-8" @submit.prevent="loginFunc">

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
        placeholder="Ваш Пароль"
        :error="errors.password"
      />

      <p v-if="errors.general" class="text-red-500 text-center">
        {{ errors.general }}
      </p>

      <div class="flex justify-between items-center">
        <label class="flex items-center gap-3">
          <input v-model="remember" type="checkbox" />
          Запомнить меня
        </label>

        <a href="#" class="text-red-500">
          Забыли пароль?
        </a>
      </div>

      <AuthButton :disabled="loading">
        {{ loading ? 'Входим...' : 'Войти' }}
      </AuthButton>

    </form>

    <p class="text-center mt-12 text-xl md:text-2xl">
      Нет аккаунта?

      <RouterLink
        to="/register"
        class="text-red-500 font-semibold"
      >
        Зарегистрироваться
      </RouterLink>
    </p>
  </AuthLayout>
</template>
```
