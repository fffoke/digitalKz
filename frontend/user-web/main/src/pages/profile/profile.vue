<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import AppLayout from '@/components/layout/AppLayout.vue'
import Avatar from '@/components/common/Avatar.vue'
import { getMyProfile } from '@/services/users'
import { getTasks, getStats } from '@/services/tutor'

const router = useRouter()
const profile = ref(null)
const tasks = ref([])
const stats = ref(null)
const loading = ref(true)
const tab = ref('tasks')

const completed = computed(() => tasks.value.filter((t) => t.status === 'done'))

const LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1']
const levelIndex = computed(() => Math.max(0, LEVELS.indexOf(profile.value?.level || 'A1')))

const RANKS = ['Бастауыш', 'Орта', 'Жетік', 'Шебер', 'Ұстаз']
const rankIndex = computed(() => Math.max(0, RANKS.indexOf(profile.value?.rank || 'Бастауыш')))

const DIFF_LABEL = { easy: 'Лёгкие', medium: 'Средние', hard: 'Сложные' }
const scoreColor = (v) =>
  v >= 75 ? 'text-green-600' : v >= 50 ? 'text-amber-600' : 'text-red-500'

onMounted(async () => {
  try {
    profile.value = (await getMyProfile()).data
    try { tasks.value = (await getTasks()).data } catch { /* нет заданий — ок */ }
    try { stats.value = (await getStats()).data } catch { /* нет статистики — ок */ }
  } catch (e) {
    console.log(e.response)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <AppLayout title="Профиль">
    <div v-if="loading" class="py-24 text-center text-gray-400">Загрузка…</div>

    <div v-else-if="profile" class="px-3 sm:px-4 py-4 space-y-4">
      <!-- шапка -->
      <div class="bg-white dark:bg-neutral-900 rounded-2xl border border-gray-100
                  dark:border-neutral-800 p-5 flex flex-col items-center text-center">
        <Avatar :name="profile.name" :src="profile.avatar" size="h-24 w-24" />

        <h2 class="mt-3 text-xl font-bold text-gray-900 dark:text-white">{{ profile.name }}</h2>
        <p class="text-red-500 text-sm">
          {{ profile.username ? '@' + profile.username : 'добавьте имя пользователя' }}
        </p>
        <p v-if="profile.bio" class="mt-2 text-sm text-gray-600 dark:text-gray-300">{{ profile.bio }}</p>

        <button
          class="mt-5 w-full bg-gray-100 dark:bg-neutral-800 text-gray-700 dark:text-gray-200
                 font-semibold rounded-xl py-2.5 text-sm hover:bg-gray-200
                 dark:hover:bg-neutral-700 transition"
          @click="router.push('/profile/edit')"
        >
          Редактировать профиль
        </button>

        <button
          v-if="profile.role !== 'teacher'"
          class="mt-2 w-full bg-red-500 hover:bg-red-600 text-white font-semibold
                 rounded-xl py-2.5 text-sm transition flex items-center justify-center gap-2"
          @click="router.push('/profile/certificate')"
        >
          🎓 Скачать сертификат
        </button>
      </div>

      <!-- ранг -->
      <div class="bg-white dark:bg-neutral-900 rounded-2xl border border-gray-100
                  dark:border-neutral-800 p-4">
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm font-semibold text-gray-900 dark:text-white">Ранг</span>
          <span class="px-2.5 py-0.5 rounded-full bg-purple-100 text-purple-700 text-xs font-bold">
            {{ profile.rank || 'Бастауыш' }}
          </span>
        </div>
        <div class="flex gap-1.5">
          <div v-for="(r, i) in RANKS" :key="r" class="flex-1 text-center">
            <div class="h-1.5 rounded-full transition-colors"
              :class="i <= rankIndex ? 'bg-purple-500' : 'bg-gray-100 dark:bg-neutral-800'" />
            <span class="text-[10px] mt-1 block truncate"
              :class="i <= rankIndex ? 'text-purple-500 font-medium' : 'text-gray-400'">{{ r }}</span>
          </div>
        </div>
      </div>

      <!-- уровень казахского -->
      <div class="bg-white dark:bg-neutral-900 rounded-2xl border border-gray-100
                  dark:border-neutral-800 p-4">
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm font-semibold text-gray-900 dark:text-white">Уровень казахского</span>
          <span class="px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-700 text-xs font-bold">
            {{ profile.level || 'A1' }}
          </span>
        </div>
        <div class="flex gap-1.5">
          <div v-for="(lvl, i) in LEVELS" :key="lvl" class="flex-1 text-center">
            <div class="h-1.5 rounded-full transition-colors"
              :class="i <= levelIndex ? 'bg-red-500' : 'bg-gray-100 dark:bg-neutral-800'" />
            <span class="text-[10px] mt-1 block"
              :class="i <= levelIndex ? 'text-red-500 font-medium' : 'text-gray-400'">{{ lvl }}</span>
          </div>
        </div>
      </div>

      <!-- подвкладки -->
      <div class="bg-white dark:bg-neutral-900 rounded-2xl border border-gray-100
                  dark:border-neutral-800 overflow-hidden">
        <div class="flex border-b border-gray-100 dark:border-neutral-800">
          <button
            class="flex-1 py-3 text-sm font-medium transition"
            :class="tab === 'tasks' ? 'text-red-500 border-b-2 border-red-500' : 'text-gray-400'"
            @click="tab = 'tasks'"
          >
            Задания
          </button>
          <button
            class="flex-1 py-3 text-sm font-medium transition"
            :class="tab === 'stats' ? 'text-red-500 border-b-2 border-red-500' : 'text-gray-400'"
            @click="tab = 'stats'"
          >
            Статистика
          </button>
        </div>

        <!-- вкладка: пройденные задания -->
        <div v-if="tab === 'tasks'">
          <div v-if="completed.length" class="divide-y divide-gray-50 dark:divide-neutral-800">
            <div v-for="t in completed" :key="t.id" class="px-4 py-3 flex items-center gap-3">
              <span class="text-lg">✅</span>
              <span class="flex-1 text-sm text-gray-700 dark:text-gray-200 truncate">{{ t.title }}</span>
              <span v-if="t.speaking_score != null"
                class="text-xs font-semibold" :class="scoreColor(t.speaking_score)">
                {{ t.speaking_score }}/100
              </span>
            </div>
          </div>
          <div v-else class="py-12 text-center text-gray-400 text-sm">
            Ещё нет пройденных заданий
          </div>
        </div>

        <!-- вкладка: статистика -->
        <div v-else class="p-4 space-y-4">
          <template v-if="stats && stats.done > 0">
            <!-- средний SpeakingScore крупно -->
            <div class="text-center py-2">
              <div class="text-4xl font-bold" :class="scoreColor(stats.avg_speaking)">
                {{ stats.avg_speaking }}<span class="text-lg text-gray-400">/100</span>
              </div>
              <p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">средний SpeakingScore</p>
            </div>

            <!-- карточки -->
            <div class="grid grid-cols-3 gap-2 text-center">
              <div class="bg-gray-50 dark:bg-neutral-800 rounded-xl py-3">
                <div class="text-lg font-bold text-gray-900 dark:text-white">{{ stats.done }}</div>
                <div class="text-[11px] text-gray-400">пройдено</div>
              </div>
              <div class="bg-gray-50 dark:bg-neutral-800 rounded-xl py-3">
                <div class="text-lg font-bold text-green-600">{{ stats.best_speaking }}</div>
                <div class="text-[11px] text-gray-400">лучший</div>
              </div>
              <div class="bg-gray-50 dark:bg-neutral-800 rounded-xl py-3">
                <div class="text-lg font-bold text-gray-900 dark:text-white">{{ stats.avg_task }}%</div>
                <div class="text-[11px] text-gray-400">выполнение</div>
              </div>
            </div>

            <!-- по сложности -->
            <div class="space-y-2">
              <p class="text-xs font-semibold text-gray-500 dark:text-gray-400">По сложности</p>
              <div v-for="d in stats.by_difficulty" :key="d.difficulty"
                class="flex items-center gap-3">
                <span class="w-16 text-xs text-gray-500">{{ DIFF_LABEL[d.difficulty] }}</span>
                <div class="flex-1 h-2 rounded-full bg-gray-100 dark:bg-neutral-800 overflow-hidden">
                  <div class="h-full rounded-full bg-red-500" :style="{ width: d.avg_speaking + '%' }" />
                </div>
                <span class="text-xs text-gray-400 w-16 text-right">
                  {{ d.done ? d.avg_speaking + '/100' : '—' }}
                </span>
              </div>
            </div>
          </template>

          <div v-else class="py-12 text-center text-gray-400 text-sm">
            Пройдите задание — здесь появится статистика
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
