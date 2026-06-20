<script setup>
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'

import AppLayout from '@/components/layout/AppLayout.vue'
import WordOfDayCard from '@/components/feed/WordOfDayCard.vue'
import PostComposer from '@/components/feed/PostComposer.vue'
import PostCard from '@/components/feed/PostCard.vue'

const user = useUserStore()
const composerPrefill = ref('')

// демо-данные (позже заменим на GET /api/posts)
const posts = ref([
  { author: 'Айгерим', time: '10 мин', likes: 24, comments: 5, reposts: 3,
    text: 'Бүгін қазақ тілі сабағында өте қызықты тақырыптарды талқыладық. Тіл үйрену — ең үлкен инвестиция! 💪' },
  { author: 'Ерлан', time: '30 мин', likes: 18, comments: 12, reposts: 2,
    text: 'Достар, Астанаға келетін қонақтар үшін қандай жерлерді ұсынады екенсіздер? Ұсыныстарыңызды жазыңыздар! 🙂' },
  { author: 'Дина', time: '1 сағ', likes: 36, comments: 7, reposts: 4,
    text: 'Жаңа кітап алып жатырмын. Қазақ әдебиетін қандай сіздерге? 📚' },
  { author: 'Нұрбек', time: '2 сағ', likes: 28, comments: 3, reposts: 1,
    text: 'Бүгін тағы уақытым. Табиғаттағы үнемі таранған жақсы екен! 🌲' },
])

const publish = (text) => {
  posts.value.unshift({
    author: user.user?.name || 'Сіз',
    time: 'сейчас',
    likes: 0, comments: 0, reposts: 0,
    text,
  })
}

const acceptChallenge = (word) => {
  composerPrefill.value = `${word} — `
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <AppLayout title="Дом">
    <div class="px-3 sm:px-4 py-4 space-y-4">
      <!-- Поиск -->
      <div class="relative">
        <svg class="h-5 w-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
          fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round"
            d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
        </svg>
        <input
          type="text"
          placeholder="Поиск"
          class="w-full rounded-xl bg-white dark:bg-neutral-900 border border-gray-100
                 dark:border-neutral-800 pl-10 pr-4 py-2.5 text-sm text-gray-900
                 dark:text-white placeholder-gray-400 focus:outline-none
                 focus:ring-2 focus:ring-red-200"
        />
      </div>

      <WordOfDayCard @compose="acceptChallenge" />

      <PostComposer :prefill="composerPrefill" @publish="publish" />

      <div class="space-y-3">
        <PostCard v-for="(post, i) in posts" :key="i" :post="post" />
      </div>
    </div>
  </AppLayout>
</template>
