<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import AppLayout from '@/components/layout/AppLayout.vue'
import Avatar from '@/components/common/Avatar.vue'
import { getMyProfile } from '@/services/users'

const router = useRouter()
const profile = ref(null)
const loading = ref(true)
const tab = ref('posts')

const tabs = [
  { key: 'posts', label: 'Посты' },
  { key: 'replies', label: 'Ответы' },
  { key: 'reposts', label: 'Репосты' },
]

onMounted(async () => {
  try {
    profile.value = (await getMyProfile()).data
  } catch (e) {
    console.log(e.response)
  } finally {
    loading.value = false
  }
})

const share = async () => {
  const handle = profile.value?.username
  const url = window.location.origin + (handle ? `/u/${handle}` : '/profile')
  if (navigator.share) {
    try { await navigator.share({ title: 'TILDES', url }) } catch {}
  } else {
    try { await navigator.clipboard.writeText(url) } catch {}
  }
}
</script>

<template>
  <AppLayout title="Профиль">
    <div v-if="loading" class="py-24 text-center text-gray-400">Загрузка…</div>

    <div v-else-if="profile" class="px-3 sm:px-4 py-4 space-y-4">
      <!-- шапка -->
      <div class="bg-white dark:bg-neutral-900 rounded-2xl border border-gray-100
                  dark:border-neutral-800 p-5 flex flex-col items-center text-center">
        <Avatar :name="profile.name" :src="profile.avatar" size="h-24 w-24" />

        <h2 class="mt-3 text-xl font-bold text-gray-900 dark:text-white">
          {{ profile.name }}
        </h2>
        <p class="text-red-500 text-sm">
          {{ profile.username ? '@' + profile.username : 'добавьте имя пользователя' }}
        </p>

        <p v-if="profile.bio" class="mt-2 text-sm text-gray-600 dark:text-gray-300">
          {{ profile.bio }}
        </p>

        <!-- бейджи уровня/ранга -->
        <div v-if="profile.level || profile.rank" class="mt-3 flex gap-2">
          <span v-if="profile.level"
            class="px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-700 text-xs font-medium">
            {{ profile.level }}
          </span>
          <span v-if="profile.rank"
            class="px-2.5 py-0.5 rounded-full bg-purple-100 text-purple-700 text-xs font-medium">
            {{ profile.rank }}
          </span>
        </div>

        <!-- счётчики -->
        <div class="mt-4 flex gap-8">
          <div class="text-center">
            <div class="text-lg font-bold text-gray-900 dark:text-white">{{ profile.followers }}</div>
            <div class="text-xs text-gray-400">подписчиков</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-bold text-gray-900 dark:text-white">{{ profile.following }}</div>
            <div class="text-xs text-gray-400">подписки</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-bold text-gray-900 dark:text-white">{{ profile.posts_count }}</div>
            <div class="text-xs text-gray-400">постов</div>
          </div>
        </div>

        <!-- кнопки -->
        <div class="mt-5 flex gap-3 w-full">
          <button
            class="flex-1 bg-gray-100 dark:bg-neutral-800 text-gray-700 dark:text-gray-200
                   font-semibold rounded-xl py-2.5 text-sm hover:bg-gray-200
                   dark:hover:bg-neutral-700 transition"
            @click="router.push('/profile/edit')"
          >
            Редактировать профиль
          </button>
          <button
            class="flex-1 bg-red-500 hover:bg-red-600 text-white font-semibold
                   rounded-xl py-2.5 text-sm transition"
            @click="share"
          >
            Поделиться
          </button>
        </div>
      </div>

      <!-- вкладки -->
      <div class="bg-white dark:bg-neutral-900 rounded-2xl border border-gray-100
                  dark:border-neutral-800 overflow-hidden">
        <div class="flex border-b border-gray-100 dark:border-neutral-800">
          <button
            v-for="t in tabs" :key="t.key"
            class="flex-1 py-3 text-sm font-medium transition"
            :class="tab === t.key
              ? 'text-red-500 border-b-2 border-red-500'
              : 'text-gray-400'"
            @click="tab = t.key"
          >
            {{ t.label }}
          </button>
        </div>

        <div class="py-16 text-center text-gray-400 text-sm">
          Пока пусто
        </div>
      </div>
    </div>
  </AppLayout>
</template>
