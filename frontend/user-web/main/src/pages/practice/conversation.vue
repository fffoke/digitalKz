<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'

import RecordButton from '@/components/tutor/RecordButton.vue'
import VoiceMessage from '@/components/tutor/VoiceMessage.vue'
import AiBubble from '@/components/tutor/AiBubble.vue'
import ResultCard from '@/components/tutor/ResultCard.vue'
import { useTutorStore } from '@/stores/tutor'

const route = useRoute()
const router = useRouter()
const tutor = useTutorStore()
const { session, turns, sending, result, finishing } = storeToRefs(tutor)

const loading = ref(true)
const error = ref('')
const scroller = ref(null)

const scrollDown = async () => {
  await nextTick()
  scroller.value?.scrollTo({ top: scroller.value.scrollHeight, behavior: 'smooth' })
}

onMounted(async () => {
  try {
    await tutor.start(route.params.taskId)
  } catch (e) {
    console.log(e.response)
    error.value = 'Не удалось начать диалог'
  } finally {
    loading.value = false
    scrollDown()
  }
})

watch(() => turns.value.length, scrollDown)
watch(sending, scrollDown)

const onRecorded = async (blob, sec) => {
  try {
    await tutor.send(blob, sec)
  } catch (e) {
    console.log(e.response)
  }
}

const onFinish = async () => {
  try {
    await tutor.finish()
    scrollDown()
  } catch (e) {
    console.log(e.response)
  }
}

const back = () => router.push({ name: 'practice' })

onBeforeUnmount(() => tutor.reset())
</script>

<template>
  <div class="h-screen flex flex-col bg-gray-50 dark:bg-neutral-950">
    <!-- шапка: задание -->
    <header class="shrink-0 sticky top-0 z-10 bg-white/90 dark:bg-neutral-900/90 backdrop-blur
                   border-b border-gray-100 dark:border-neutral-800">
      <div class="max-w-xl mx-auto flex items-center gap-2 h-14 px-3">
        <button class="p-2 -ml-1 rounded-full text-gray-500 hover:bg-gray-100 dark:hover:bg-neutral-800"
          @click="back">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
          </svg>
        </button>
        <div class="min-w-0 flex-1">
          <p class="text-[11px] text-gray-400 leading-none">Задание</p>
          <h1 class="text-sm font-semibold text-gray-900 dark:text-white truncate">
            {{ session?.task?.title || 'Диалог с ИИ' }}
          </h1>
        </div>
        <button
          v-if="session && session.status === 'active'"
          class="px-3 py-1.5 rounded-full bg-gray-100 dark:bg-neutral-800 text-xs font-medium
                 text-gray-600 dark:text-gray-300 disabled:opacity-50"
          :disabled="finishing || sending"
          @click="onFinish"
        >
          {{ finishing ? '…' : 'Завершить' }}
        </button>
      </div>
    </header>

    <!-- лента диалога -->
    <main ref="scroller" class="flex-1 overflow-y-auto">
      <div class="max-w-xl mx-auto px-3 sm:px-4 py-4 space-y-3">
        <div v-if="loading" class="py-24 text-center text-gray-400">Загрузка…</div>
        <p v-else-if="error" class="py-24 text-center text-red-400">{{ error }}</p>

        <template v-else>
          <!-- описание задания: что нужно сделать -->
          <div v-if="session?.task?.description"
            class="bg-white dark:bg-neutral-900 border border-gray-100 dark:border-neutral-800
                   rounded-2xl p-4">
            <div class="flex items-center gap-2 mb-1.5">
              <span class="text-base">🎯</span>
              <span class="text-xs font-semibold text-red-500 uppercase tracking-wide">Ваше задание</span>
            </div>
            <p class="text-sm text-gray-700 dark:text-gray-200 leading-relaxed">
              {{ session.task.description }}
            </p>
          </div>

          <template v-for="t in turns" :key="t.id">
            <AiBubble v-if="t.role === 'ai'" :text="t.text" />
            <VoiceMessage
              v-else
              :src="t.audioUrl"
              :duration="t.duration"
              :transcript="t.transcript"
              :pending="t.pending"
              :failed="t.failed"
              mine
            />
          </template>

          <AiBubble v-if="sending" typing />
        </template>
      </div>
    </main>

    <!-- панель записи / результат -->
    <footer class="shrink-0 border-t border-gray-100 dark:border-neutral-800
                   bg-white dark:bg-neutral-900">
      <div class="max-w-xl mx-auto px-4 py-4">
        <ResultCard v-if="result" :result="result" @close="back" />
        <div v-else class="flex justify-center">
          <RecordButton :disabled="sending || loading || !session" @recorded="onRecorded" />
        </div>
      </div>
    </footer>
  </div>
</template>
