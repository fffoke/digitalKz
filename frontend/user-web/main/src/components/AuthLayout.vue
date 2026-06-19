<script setup>
import AppLogo from './AppLogo.vue'

defineProps({
  title: String,
  subtitle: String
})
</script>

<template>
  <div class="min-h-screen bg-[#f7f7f7]">
    <div
      class="w-full max-w-md md:max-w-lg lg:max-w-xl mx-auto px-6 py-10 md:py-16"
    >
      <AppLogo />

      <h1
        class="mt-10 md:mt-16
               text-3xl md:text-5xl lg:text-6xl
               font-bold
               leading-tight"
      >
        {{ title }}
      </h1>

      <p
        class="mt-3
               text-md md:text-xl
               text-gray-500"
      >
        {{ subtitle }}
      </p>

      <div class="mt-10">
        <slot />
      </div>
    </div>
  </div>
</template>