<script setup>
import { ref } from 'vue'
import Avatar from '@/components/common/Avatar.vue'

const props = defineProps({
  post: { type: Object, required: true },
})

const liked = ref(false)
const likes = ref(props.post.likes ?? 0)

const toggleLike = () => {
  liked.value = !liked.value
  likes.value += liked.value ? 1 : -1
}
</script>

<template>
  <article class="bg-white dark:bg-neutral-900 rounded-2xl border border-gray-100
                  dark:border-neutral-800 p-3 sm:p-4">
    <div class="flex gap-3">
      <Avatar :name="post.author" :src="post.avatar" />

      <div class="flex-1 min-w-0">
        <div class="flex items-center justify-between gap-2">
          <span class="font-semibold text-gray-900 dark:text-white truncate">
            {{ post.author }}
          </span>
          <span class="text-xs text-gray-400 shrink-0">{{ post.time }}</span>
        </div>

        <p class="mt-1 text-sm sm:text-[15px] text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
          {{ post.text }}
        </p>

        <div class="mt-3 flex items-center gap-6 text-gray-400">
          <button
            class="flex items-center gap-1.5 text-xs hover:text-red-500 transition"
            :class="liked && 'text-red-500'"
            @click="toggleLike"
          >
            <svg class="h-5 w-5" :fill="liked ? 'currentColor' : 'none'" viewBox="0 0 24 24"
              stroke-width="1.6" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z" />
            </svg>
            {{ likes }}
          </button>

          <button class="flex items-center gap-1.5 text-xs hover:text-gray-600 transition">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 0 1 .865-.501 48.172 48.172 0 0 0 3.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z" />
            </svg>
            {{ post.comments ?? 0 }}
          </button>

          <button class="flex items-center gap-1.5 text-xs hover:text-green-600 transition">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M19.5 12c0-1.232-.046-2.453-.138-3.662a4.006 4.006 0 0 0-3.7-3.7 48.678 48.678 0 0 0-7.324 0 4.006 4.006 0 0 0-3.7 3.7c-.017.22-.032.441-.046.662M19.5 12l3-3m-3 3-3-3m-12 3c0 1.232.046 2.453.138 3.662a4.006 4.006 0 0 0 3.7 3.7 48.656 48.656 0 0 0 7.324 0 4.006 4.006 0 0 0 3.7-3.7c.017-.22.032-.441.046-.662M4.5 12l3 3m-3-3-3 3" />
            </svg>
            {{ post.reposts ?? 0 }}
          </button>

          <button class="ml-auto hover:text-red-500 transition">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.6" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M3 3v1.5M3 21v-6m0 0 2.77-.693a9 9 0 0 1 6.208.682l.108.054a9 9 0 0 0 6.086.71l3.114-.732a48.524 48.524 0 0 1-.005-10.499l-3.11.732a9 9 0 0 1-6.085-.711l-.108-.054a9 9 0 0 0-6.208-.682L3 4.5M3 15V4.5" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </article>
</template>
