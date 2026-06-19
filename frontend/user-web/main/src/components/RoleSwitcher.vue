<script setup>
defineProps({
  modelValue: String,
})

defineEmits(['update:modelValue'])
</script>

<template>
  <div
    class="bg-gray-100 border rounded-full p-1 flex mb-12"
  >
    <button
      class="flex-1 py-3 rounded-full font-semibold"
      :class="modelValue === 'student'
        ? 'bg-white shadow'
        : 'text-gray-500'"
      @click="$emit('update:modelValue','student')"
    >
      Ученик
    </button>

    <button
      class="flex-1 py-3 rounded-full font-semibold"
      :class="modelValue === 'teacher'
        ? 'bg-white shadow'
        : 'text-gray-500'"
      @click="$emit('update:modelValue','teacher')"
    >
      Преподаватель
    </button>
  </div>
</template>