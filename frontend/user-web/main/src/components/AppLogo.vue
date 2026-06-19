<template>
  <RouterLink :to="{ name: 'landing' }">
    <div class="flex items-center gap-4">
        <div
        class="w-10 h-10 md:w-16 md:h-16 rounded-2xl bg-red-500 text-white flex items-center justify-center font-bold text-lg md:text-3xl"
        >
        T
        </div>

        <span class="text-xl md:text-4xl font-semibold">
        ТІЛДЕС
        </span>
    </div>
  </RouterLink>
</template>