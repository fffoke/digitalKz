<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount } from 'vue'
import Avatar from '@/components/common/Avatar.vue'
import { getGroupMessages, sendGroupMessage } from '@/services/learning'

const props = defineProps({
  groupId: { type: Number, required: true },
  height: { type: String, default: '26rem' },
  bare: { type: Boolean, default: false },  // без рамки/заголовка — для полного экрана
})

const messages = ref([])
const text = ref('')
const loading = ref(true)
const sending = ref(false)
const box = ref(null)

let timer = null

const scrollDown = async () => {
  await nextTick()
  if (box.value) box.value.scrollTop = box.value.scrollHeight
}

const load = async (initial = false) => {
  try {
    const { data } = await getGroupMessages(props.groupId)
    const grew = data.length !== messages.value.length
    messages.value = data
    if (initial || grew) scrollDown()
  } catch (e) {
    console.log(e.response)
  } finally {
    loading.value = false
  }
}

const send = async () => {
  const t = text.value.trim()
  if (!t || sending.value) return
  sending.value = true
  text.value = ''
  try {
    const { data } = await sendGroupMessage(props.groupId, t)
    messages.value.push(data)
    scrollDown()
  } catch (e) {
    console.log(e.response)
    text.value = t // вернуть текст при ошибке
  } finally {
    sending.value = false
  }
}

const fmt = (iso) => {
  const d = new Date(iso)
  return d.toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  load(true)
  timer = setInterval(load, 4000) // лёгкий опрос новых сообщений
})
onBeforeUnmount(() => clearInterval(timer))
</script>

<template>
  <div class="overflow-hidden flex flex-col bg-white dark:bg-neutral-900"
       :class="bare ? '' : 'rounded-2xl border border-gray-100 dark:border-neutral-800'"
       :style="{ height }">
    <div v-if="!bare" class="px-4 py-3 border-b border-gray-100 dark:border-neutral-800 flex items-center gap-2">
      <span class="text-lg">💬</span>
      <span class="text-sm font-semibold text-gray-900 dark:text-white">Чат группы</span>
    </div>

    <!-- лента -->
    <div ref="box" class="flex-1 overflow-y-auto px-3 py-3 space-y-2.5 bg-gray-50 dark:bg-neutral-950">
      <p v-if="loading" class="text-center text-gray-400 text-sm py-8">Загрузка…</p>
      <p v-else-if="!messages.length" class="text-center text-gray-400 text-sm py-8">
        Сообщений пока нет — напишите первым
      </p>

      <div v-for="m in messages" :key="m.id" class="flex items-end gap-2"
           :class="m.is_mine ? 'justify-end' : 'justify-start'">
        <!-- аватар отправителя (для чужих — слева) -->
        <Avatar v-if="!m.is_mine" :name="m.sender_name" :src="m.sender_avatar" size="h-8 w-8" class="mb-4" />

        <div class="max-w-[75%]">
          <p v-if="!m.is_mine" class="text-[11px] text-gray-400 mb-0.5 pl-1">{{ m.sender_name }}</p>
          <div class="px-3 py-2 rounded-2xl text-sm break-words"
               :class="m.is_mine
                 ? 'bg-red-500 text-white rounded-br-md'
                 : 'bg-white dark:bg-neutral-800 text-gray-800 dark:text-gray-100 rounded-bl-md border border-gray-100 dark:border-neutral-700'">
            {{ m.text }}
            <span class="block text-[10px] mt-0.5" :class="m.is_mine ? 'text-white/70 text-right' : 'text-gray-400'">
              {{ fmt(m.created_at) }}
            </span>
          </div>
        </div>

        <!-- мой аватар справа -->
        <Avatar v-if="m.is_mine" :name="m.sender_name" :src="m.sender_avatar" size="h-8 w-8" class="mb-4" />
      </div>
    </div>

    <!-- ввод -->
    <form class="p-3 border-t border-gray-100 dark:border-neutral-800 flex gap-2" @submit.prevent="send">
      <input
        v-model="text" placeholder="Сообщение…" maxlength="2000"
        class="flex-1 rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800
               text-gray-900 dark:text-white placeholder:text-gray-400 px-3 py-2.5 text-sm focus:border-red-400 focus:outline-none"
      />
      <button type="submit" :disabled="sending || !text.trim()"
        class="px-4 rounded-xl bg-red-500 hover:bg-red-600 disabled:opacity-40 text-white text-sm font-semibold transition">
        ➤
      </button>
    </form>
  </div>
</template>
