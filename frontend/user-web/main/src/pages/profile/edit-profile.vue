<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import AppLayout from '@/components/layout/AppLayout.vue'
import AuthInput from '@/components/AuthInput.vue'
import Avatar from '@/components/common/Avatar.vue'
import { useUserStore } from '@/stores/user'
import { getMyProfile, updateProfile, uploadAvatar } from '@/services/users'

const router = useRouter()
const userStore = useUserStore()

const form = reactive({ name: '', username: '', bio: '', avatar: '' })
const error = ref('')
const loading = ref(false)
const uploading = ref(false)
const fileInput = ref(null)

onMounted(async () => {
  const p = (await getMyProfile()).data
  form.name = p.name || ''
  form.username = p.username || ''
  form.bio = p.bio || ''
  form.avatar = p.avatar || ''
})

const onAvatarPick = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  uploading.value = true
  error.value = ''
  try {
    const p = (await uploadAvatar(file)).data
    form.avatar = p.avatar
    await userStore.fetchUser()
  } catch (err) {
    error.value = 'Не удалось загрузить фото'
  } finally {
    uploading.value = false
  }
}

const save = async () => {
  error.value = ''
  try {
    loading.value = true
    await updateProfile({
      name: form.name,
      username: form.username || null,
      bio: form.bio || null,
      avatar: form.avatar || null,
    })
    await userStore.fetchUser()
    router.push('/profile')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось сохранить'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppLayout title="Редактировать">
    <div class="px-4 py-4 space-y-6">
      <div class="flex items-center justify-between">
        <button class="text-gray-500 dark:text-gray-300" @click="router.back()">
          ← Назад
        </button>
      </div>

      <!-- аватар -->
      <div class="flex flex-col items-center gap-3">
        <Avatar :name="form.name" :src="form.avatar" size="h-24 w-24" />
        <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onAvatarPick" />
        <button
          class="text-sm font-medium text-red-500 disabled:opacity-50"
          :disabled="uploading"
          @click="fileInput.click()"
        >
          {{ uploading ? 'Загрузка…' : 'Загрузить фото' }}
        </button>
      </div>

      <AuthInput v-model="form.name" label="Имя" placeholder="Адильжан" />
      <AuthInput v-model="form.username" label="Имя пользователя" placeholder="adilzhan" />

      <div>
        <label class="block mb-2 text-base font-medium text-gray-800 dark:text-gray-200">
          О себе
        </label>
        <textarea
          v-model="form.bio"
          rows="3"
          placeholder="Қазақ тілін үйренемін…"
          class="w-full rounded-2xl bg-white dark:bg-neutral-900 border border-gray-200
                 dark:border-neutral-700 px-4 py-3 text-gray-900 dark:text-white
                 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-200"
        />
      </div>

      <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>

      <button
        class="w-full bg-red-500 hover:bg-red-600 disabled:opacity-40 text-white
               font-semibold rounded-full py-3.5 text-lg transition"
        :disabled="loading"
        @click="save"
      >
        {{ loading ? 'Сохранение…' : 'Сохранить' }}
      </button>
    </div>
  </AppLayout>
</template>
