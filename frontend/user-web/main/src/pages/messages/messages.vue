<script setup>
import { ref, watch } from 'vue'

import AppLayout from '@/components/layout/AppLayout.vue'
import Avatar from '@/components/common/Avatar.vue'
import { getNotifications } from '@/services/notifications'

const sub = ref('messages') // messages | activity
const filter = ref('all')   // all | follows | mentions
const notifications = ref([])
const loading = ref(false)

const filters = [
  { key: 'all', label: 'Все' },
  { key: 'follows', label: 'Подписки' },
  { key: 'mentions', label: 'Упоминания' },
]

const labelByType = {
  like: 'лайкнул(а) ваш пост',
  follow: 'подписался(ась) на вас',
  comment: 'прокомментировал(а) ваш пост',
  mention: 'упомянул(а) вас',
  repost: 'репостнул(а) ваш пост',
  role_granted: 'Поздравляем! Вам выдана новая роль 🎉',
  role_rejected: 'Заявка на роль отклонена',
}

const loadActivity = async () => {
  loading.value = true
  try {
    notifications.value = (await getNotifications(filter.value)).data
  } catch (e) {
    console.log(e.response)
  } finally {
    loading.value = false
  }
}

watch(
  [sub, filter],
  () => { if (sub.value === 'activity') loadActivity() },
  { immediate: false },
)
</script>

<template>
  <AppLayout title="Директ">
    <div class="px-3 sm:px-4 py-4 space-y-4">
      <!-- подвкладки -->
      <div class="flex bg-gray-100 dark:bg-neutral-800 rounded-full p-1">
        <button
          class="flex-1 py-2 rounded-full text-sm font-semibold transition"
          :class="sub === 'messages' ? 'bg-white dark:bg-neutral-900 shadow text-gray-900 dark:text-white' : 'text-gray-500'"
          @click="sub = 'messages'"
        >
          Сообщения
        </button>
        <button
          class="flex-1 py-2 rounded-full text-sm font-semibold transition"
          :class="sub === 'activity' ? 'bg-white dark:bg-neutral-900 shadow text-gray-900 dark:text-white' : 'text-gray-500'"
          @click="sub = 'activity'"
        >
          Активность
        </button>
      </div>

      <!-- СООБЩЕНИЯ -->
      <div v-if="sub === 'messages'" class="py-16 text-center text-gray-400 text-sm">
        Личные сообщения скоро появятся
      </div>

      <!-- АКТИВНОСТЬ -->
      <div v-else class="space-y-3">
        <div class="flex gap-2">
          <button
            v-for="f in filters" :key="f.key"
            class="px-3 py-1.5 rounded-full text-xs font-medium transition"
            :class="filter === f.key
              ? 'bg-red-500 text-white'
              : 'bg-gray-100 dark:bg-neutral-800 text-gray-500'"
            @click="filter = f.key"
          >
            {{ f.label }}
          </button>
        </div>

        <div v-if="loading" class="py-12 text-center text-gray-400 text-sm">Загрузка…</div>

        <div v-else-if="!notifications.length" class="py-12 text-center text-gray-400 text-sm">
          Пока нет событий
        </div>

        <div v-else class="space-y-2">
          <div
            v-for="n in notifications" :key="n.id"
            class="bg-white dark:bg-neutral-900 rounded-2xl border border-gray-100
                   dark:border-neutral-800 p-3 flex items-center gap-3"
          >
            <Avatar :name="'?'" size="h-10 w-10" />
            <p class="text-sm text-gray-700 dark:text-gray-200">
              {{ labelByType[n.type] || n.type }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
