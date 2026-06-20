<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AppLayout from '@/components/layout/AppLayout.vue'
import { useUserStore } from '@/stores/user'
import { getDuel, answerDuel } from '@/services/duels'

const route = useRoute()
const router = useRouter()
const user = useUserStore()

const duel = ref(null)
const answer = ref('')
const submitted = ref(false)
let poll = null

const myId = computed(() => user.user?.id)
const isFinished = computed(() => duel.value?.status === 'finished')
const iWon = computed(() => isFinished.value && duel.value.winner_id === myId.value)

const load = async () => {
  duel.value = (await getDuel(route.params.id)).data
}

onMounted(load)
onUnmounted(() => poll && clearInterval(poll))

const send = async () => {
  if (!answer.value.trim()) return
  duel.value = (await answerDuel(route.params.id, answer.value.trim())).data
  submitted.value = true
  if (duel.value.status !== 'finished') {
    poll = setInterval(async () => {
      await load()
      if (duel.value.status === 'finished') clearInterval(poll)
    }, 2000)
  }
}
</script>

<template>
  <AppLayout title="Дуэль">
    <div v-if="duel" class="px-3 sm:px-4 py-4 space-y-4">
      <!-- задание -->
      <div class="rounded-2xl p-5 bg-white dark:bg-neutral-900 border border-gray-100
                  dark:border-neutral-800">
        <div class="text-xs font-medium text-red-500">Задание</div>
        <p class="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
          {{ duel.prompt }}
        </p>
      </div>

      <!-- результат -->
      <div
        v-if="isFinished"
        class="rounded-2xl p-6 text-center text-white"
        :class="iWon ? 'bg-green-500' : 'bg-gray-500'"
      >
        <div class="text-2xl font-bold">{{ iWon ? '🏆 Победа!' : 'Поражение' }}</div>
        <div class="mt-1 text-white/90 text-sm">
          Счёт: {{ duel.score1 }} : {{ duel.score2 }}
        </div>
        <button
          class="mt-4 bg-white/20 hover:bg-white/30 rounded-xl px-5 py-2 text-sm font-semibold"
          @click="router.push('/duels')"
        >
          К дуэлям
        </button>
      </div>

      <!-- ввод ответа -->
      <div v-else-if="!submitted"
        class="rounded-2xl p-4 bg-white dark:bg-neutral-900 border border-gray-100
               dark:border-neutral-800 space-y-3">
        <textarea
          v-model="answer"
          rows="4"
          placeholder="Сіздің жауабыңыз…"
          class="w-full resize-none bg-transparent text-gray-900 dark:text-white
                 placeholder-gray-400 focus:outline-none"
        />
        <button
          class="w-full bg-red-500 hover:bg-red-600 disabled:opacity-40 text-white
                 font-semibold rounded-xl py-3 transition"
          :disabled="!answer.trim()"
          @click="send"
        >
          Ответить
        </button>
        <p class="text-center text-xs text-gray-400">
          🎤 Голосовые ответы добавим следующим шагом
        </p>
      </div>

      <!-- ждём соперника -->
      <div v-else class="py-12 text-center text-gray-400 text-sm">
        Ответ принят. Ждём соперника…
      </div>
    </div>

    <div v-else class="py-24 text-center text-gray-400">Загрузка…</div>
  </AppLayout>
</template>
