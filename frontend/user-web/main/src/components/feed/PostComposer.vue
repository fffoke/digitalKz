<script setup>
import { ref, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import Avatar from '@/components/common/Avatar.vue'

const props = defineProps({
  prefill: { type: String, default: '' },
})

const emit = defineEmits(['publish'])
const user = useUserStore()
const text = ref('')

watch(
  () => props.prefill,
  (val) => {
    if (val) text.value = val.endsWith(' ') ? val : val + ' '
  },
)

const submit = () => {
  const value = text.value.trim()
  if (!value) return
  emit('publish', value)
  text.value = ''
}
</script>

<template>
  <div class="bg-white dark:bg-neutral-900 rounded-2xl border border-gray-100
              dark:border-neutral-800 p-3 sm:p-4">
    <div class="flex gap-3">
      <Avatar :name="user.user?.name" :src="user.user?.avatar" />

      <div class="flex-1">
        <textarea
          v-model="text"
          rows="2"
          placeholder="Поделитесь чем-нибудь…"
          class="w-full resize-none bg-transparent text-gray-900 dark:text-white
                 placeholder-gray-400 text-sm sm:text-base focus:outline-none"
        />

        <div class="flex justify-end">
          <button
            class="bg-red-500 hover:bg-red-600 disabled:opacity-40
                   text-white font-semibold rounded-xl px-5 py-2 text-sm transition"
            :disabled="!text.trim()"
            @click="submit"
          >
            Опубликовать
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
