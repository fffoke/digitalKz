<script setup>
import { ref } from 'vue'

const steps = ref([
  {
    id: '01',
    title: 'Верификация',
    text: 'ИИН и удостоверение личности. Безопасно и быстро.',
  },
  {
    id: '02',
    title: 'Вступительный тест',
    text: '25 вопросов с голосовыми заданиями. Определяем уровень A1-C1.',
  },
  {
    id: '03',
    title: 'Выбор группы',
    text: 'Поток из 2-5 учеников вашего уровня и преподаватель.',
  },
  {
    id: '04',
    title: 'Обучение',
    text: 'Живые уроки, домашние задания и социальная лента.',
  },
])

const ranks = ref([
  'Бастауыш',
  'Орта',
  'Жетік',
  'Шебер',
  'Ұстаз',
])
</script>

<template>
  <div class="bg-[#f7f7f7] min-h-screen">

    <!-- Header -->
    <header class="bg-white border-b">
      <div
        class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between"
      >
        <div class="flex items-center gap-3">
          <div
            class="w-9 h-9 rounded-xl bg-red-500 text-white flex items-center justify-center font-bold"
          >
            T
          </div>

          <span class="font-semibold">
            ТІЛДЕС
          </span>
        </div>

        <div class="flex items-center gap-4">
          <RouterLink
            to="/login"
            class="text-sm"
          >
            Войти
          </RouterLink>

          <RouterLink
            to="/register"
            class="bg-red-500 text-white px-4 py-2 rounded-full text-sm"
          >
            Начать
          </RouterLink>
        </div>
      </div>
    </header>

    <!-- Hero -->
    <section class="py-16 md:py-24">
      <div class="max-w-5xl mx-auto px-4 text-center">

        <span
          class="inline-flex px-4 py-1 rounded-full bg-red-50 text-red-500 text-xs"
        >
          • Платформа поддерживается государством
        </span>

        <h1
          class="mt-6 font-bold leading-tight
          text-5xl md:text-6xl lg:text-7xl"
        >
          Қазақ тілін

          <span class="text-red-500 block">
            үйрен.
          </span>

          Бесплатно.
        </h1>

        <p
          class="max-w-xl mx-auto mt-6 text-gray-500
          text-base md:text-lg"
        >
          Живые преподаватели, группы по 2–5 человек,
          персональный уровень и социальная лента —
          всё чтобы заговорить на казахском.
        </p>

        <div
          class="mt-10 flex flex-col sm:flex-row justify-center gap-4"
        >
          <RouterLink
            to="/register"
            class="bg-red-500 text-white px-8 py-4 rounded-full"
          >
            Стать учеником
          </RouterLink>

          <RouterLink
            to="/register"
            class="border px-8 py-4 rounded-full bg-white"
          >
            Стать преподавателем
          </RouterLink>
        </div>

        <div
          class="grid grid-cols-3 gap-6 max-w-lg mx-auto mt-16"
        >
          <div>
            <div class="text-3xl font-bold">
              100%
            </div>
            <div class="text-gray-500 text-sm">
              бесплатно
            </div>
          </div>

          <div>
            <div class="text-3xl font-bold">
              2–5
            </div>
            <div class="text-gray-500 text-sm">
              в группе
            </div>
          </div>

          <div>
            <div class="text-3xl font-bold">
              5
            </div>
            <div class="text-gray-500 text-sm">
              рангов
            </div>
          </div>
        </div>

      </div>
    </section>

    <!-- Student Path -->
    <section class="py-20 bg-white">
      <div class="max-w-7xl mx-auto px-4">

        <h2 class="text-4xl font-bold">
          Путь ученика
        </h2>

        <p class="text-gray-500 mt-3">
          Четыре шага от регистрации до свободного общения.
        </p>

        <div
          class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mt-12"
        >
          <div
            v-for="step in steps"
            :key="step.id"
            class="bg-white rounded-3xl p-8 border shadow-sm"
          >
            <div
              class="text-red-500 font-bold text-3xl"
            >
              {{ step.id }}
            </div>

            <h3
              class="font-semibold text-xl mt-4"
            >
              {{ step.title }}
            </h3>

            <p
              class="text-gray-500 mt-3 text-sm leading-6"
            >
              {{ step.text }}
            </p>
          </div>
        </div>

      </div>
    </section>

    <!-- Ranks -->
    <section class="py-20">
      <div class="max-w-5xl mx-auto px-4">

        <h2
          class="text-4xl md:text-5xl font-bold"
        >
          Ранги от Бастауыш до

          <span class="text-red-500">
            Ұстаз
          </span>
        </h2>

        <p class="text-gray-500 mt-4">
          Прозрачная система прогресса.
        </p>

        <div class="mt-10 space-y-4">
          <div
            v-for="(rank,index) in ranks"
            :key="rank"
            class="bg-white border rounded-2xl px-5 py-4 flex items-center gap-4"
          >
            <div
              class="w-8 h-8 rounded-full bg-red-50 text-red-500 flex items-center justify-center text-sm"
            >
              {{ index + 1 }}
            </div>

            <span>
              {{ rank }}
            </span>
          </div>
        </div>

      </div>
    </section>

    <!-- Teacher CTA -->
    <section class="pb-20">
      <div class="max-w-5xl mx-auto px-4">

        <div
          class="bg-[#05081A]
          rounded-[32px]
          text-center
          text-white
          px-8 py-16"
        >
          <h2
            class="text-4xl md:text-5xl font-bold max-w-2xl mx-auto"
          >
            Преподавайте —
            государство оплачивает
          </h2>

          <p
            class="mt-6 max-w-xl mx-auto text-white/70"
          >
            Работайте по принципу фриланс-биржи.
            Получайте выплаты за каждый проведённый урок.
          </p>

          <RouterLink 
            :to="{ name: 'register' }"
            class="mt-8 block bg-red-500 hover:bg-red-600 transition px-8 py-4 rounded-full"
          >
            Стать преподавателем
          </RouterLink>
        </div>

      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-white border-t">
      <div
        class="max-w-7xl mx-auto px-4 py-10"
      >
        <div class="flex items-center gap-3">
          <div
            class="w-8 h-8 rounded-full bg-red-500 text-white flex items-center justify-center text-sm"
          >
            T
          </div>

          <span class="font-medium">
            ТІЛДЕС
          </span>
        </div>

        <p
          class="text-gray-500 text-sm mt-4"
        >
          Бесплатное обучение казахскому языку.
          Поддержано государством.
        </p>

        <p
          class="text-xs text-gray-400 mt-4"
        >
          © 2026 ТІЛДЕС. Все права защищены.
        </p>
      </div>
    </footer>

  </div>
</template>