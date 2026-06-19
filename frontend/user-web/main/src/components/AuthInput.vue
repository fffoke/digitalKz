```vue id="jlwmfd"
<script setup>
defineProps({
  label: String,

  type: {
    type: String,
    default: 'text',
  },

  modelValue: String,

  placeholder: String,

  error: String,
})

defineEmits(['update:modelValue'])
</script>

<template>
  <div>
    <label
      class="block mb-3 text-xl md:text-2xl font-medium"
    >
      {{ label }}
    </label>

    <input
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      class="w-full rounded-3xl border px-5 py-3 md:px-8 md:py-4 text-lg md:text-xl outline-none transition"
      :class="[
        error
          ? 'border-red-400 focus:ring-2 focus:ring-red-400'
          : 'border-gray-200 focus:ring-2 focus:ring-red-400'
      ]"
      @input="$emit('update:modelValue', $event.target.value)"
    />

    <p
      v-if="error"
      class="mt-2 text-red-500 text-sm md:text-base"
    >
      {{ error }}
    </p>
  </div>
</template>
```
