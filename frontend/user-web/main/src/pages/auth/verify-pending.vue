<script setup>

import AuthButton from '@/components/AuthButton.vue';
import AuthLayout from '@/components/AuthLayout.vue'

</script>

<template>
  <AuthLayout
    title="Идёт Проверка Документов..."
    subtitle="Обычно проверка занимает 5–15 минуты"
  >

  <AuthButton>
    <RouterLink :to="{ name: 'verify' }">
    Отправить Заново
    </RouterLink>
  </AuthButton>
  </AuthLayout>
</template>