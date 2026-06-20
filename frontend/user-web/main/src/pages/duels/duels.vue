<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

import AppLayout from '@/components/layout/AppLayout.vue'
import Avatar from '@/components/common/Avatar.vue'
import { getMyProfile } from '@/services/users'
import { queueDuel, getDuel, getLeaderboard } from '@/services/duels'

const router = useRouter()
const rating = ref(null)
const leaderboard = ref([])
const searching = ref(false)
let poll = null

onMounted(async () => {
  rating.value = (await getMyProfile()).data.duel_rating
  leaderboard.value = (await getLeaderboard()).data
})

onUnmounted(() => poll && clearInterval(poll))

const findOpponent = async () => {
  searching.value = true
  try {
    const duel = (await queueDuel()).data
    if (duel.status === 'active') {
      router.push(`/duels/${duel.id}`)
    } else {
      // встали в очередь — ждём соперника
      poll = setInterval(async () => {
        const d = (await getDuel(duel.id)).data
        if (d.status === 'active') {
          clearInterval(poll)
          router.push(`/duels/${d.id}`)
        }
      }, 2000)
    }
  } catch (e) {
    searching.value = false
    console.log(e.response)
  }
}
</script>

<template>
  <AppLayout title="Дуэли">
    <div class="px-3 sm:px-4 py-4 space-y-4">
      <!-- рейтинг + поиск -->
      <div class="rounded-2xl p-5 text-white bg-gradient-to-br from-red-500 to-rose-600">
        <div class="flex items-center gap-2 text-white/80 text-sm font-medium">
          ⚔️ Языковая дуэль
        </div>
        <div class="mt-2 text-3xl font-bold">{{ rating ?? '—' }}</div>
        <div class="text-white/80 text-sm">ваш рейтинг</div>

        <button
          class="mt-4 w-full bg-white text-red-600 font-semibold rounded-xl py-3
                 hover:bg-red-50 transition disabled:opacity-70"
          :disabled="searching"
          @click="findOpponent"
        >
          {{ searching ? 'Ищем соперника…' : 'Найти соперника' }}
        </button>
      </div>

      <!-- лидерборд -->
      <div class="bg-white dark:bg-neutral-900 rounded-2xl border border-gray-100
                  dark:border-neutral-800 overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-100 dark:border-neutral-800
                    font-semibold text-gray-900 dark:text-white text-sm">
          🏆 Таблица лидеров
        </div>

        <div v-if="!leaderboard.length" class="py-10 text-center text-gray-400 text-sm">
          Пока пусто — сыграй первым!
        </div>

        <ul v-else>
          <li
            v-for="(u, i) in leaderboard" :key="u.id"
            class="flex items-center gap-3 px-4 py-2.5 border-b border-gray-50
                   dark:border-neutral-800 last:border-0"
          >
            <span class="w-5 text-sm font-bold text-gray-400">{{ i + 1 }}</span>
            <Avatar :name="u.name" :src="u.avatar" size="h-9 w-9" />
            <span class="flex-1 text-sm text-gray-800 dark:text-gray-200 truncate">
              {{ u.name }}
            </span>
            <span class="text-sm font-semibold text-red-500">{{ u.duel_rating }}</span>
          </li>
        </ul>
      </div>
    </div>
  </AppLayout>
</template>
