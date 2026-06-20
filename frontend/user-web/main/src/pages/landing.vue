<script setup>
const aiSteps = [
  { icon: '🎙', title: 'Запиши голос', text: 'Говоришь по-казахски на тему задания — как голосовое в Telegram.' },
  { icon: '🤖', title: 'ИИ отвечает', text: 'Живой собеседник на казахском подстраивается под твой уровень и кейс.' },
  { icon: '📊', title: 'SpeakingScore', text: 'Оценка речи из 100 баллов и разбор ошибок после каждого диалога.' },
]
const products = [
  {
    icon: '🤖', tag: 'AI практика',
    title: 'Говори с ИИ голосом',
    text: 'Персональные задания под твои интересы и уровень. Разговорная практика без стеснения — в любое время.',
    points: ['Задания easy / medium / hard под твой уровень', 'Голосовой диалог + расшифровка', 'SpeakingScore и статистика прогресса'],
  },
  {
    icon: '🎓', tag: 'Обучение',
    title: 'Группы и живые преподаватели',
    text: 'Структурный путь: верификация, уровень A1–C1, группы 2–5 человек и преподаватель.',
    points: ['Преподаватели и группы по уровню', 'Уроки и домашние задания', 'Прозрачные ранги: Бастауыш → Ұстаз'],
  },
]
</script>

<template>
  <div class="bg-gray-50 dark:bg-neutral-950 min-h-screen text-gray-900 dark:text-white">
    <!-- Header -->
    <header class="bg-white/80 dark:bg-neutral-900/80 backdrop-blur border-b
                   border-gray-100 dark:border-neutral-800 sticky top-0 z-10">
      <div class="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 rounded-xl bg-red-500 text-white flex items-center justify-center font-bold">T</div>
          <span class="font-semibold">ТІЛДЕС</span>
        </div>
        <div class="flex items-center gap-3">
          <RouterLink to="/login" class="text-sm font-medium">Войти</RouterLink>
          <RouterLink to="/register"
            class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-full text-sm font-medium transition">
            Начать
          </RouterLink>
        </div>
      </div>
    </header>

    <!-- Hero -->
    <section class="py-14 sm:py-20">
      <div class="max-w-3xl mx-auto px-4 text-center">
        <span class="inline-flex px-3 py-1 rounded-full bg-red-50 dark:bg-neutral-900
                     text-red-500 text-xs font-medium">
          🎙 Разговорный казахский с ИИ
        </span>
        <h1 class="mt-5 font-bold leading-tight text-4xl sm:text-5xl lg:text-6xl">
          Заговори на казахском
          <span class="text-red-500 block">разговаривая</span>
        </h1>
        <p class="max-w-xl mx-auto mt-5 text-gray-500 dark:text-gray-400 text-base sm:text-lg">
          Практикуй речь с ИИ-собеседником голосом — или учись в группах с живыми
          преподавателями. Бесплатно.
        </p>
        <div class="mt-8 flex flex-col sm:flex-row justify-center gap-3">
          <RouterLink to="/register"
            class="bg-red-500 hover:bg-red-600 text-white px-7 py-3.5 rounded-full font-medium transition">
            Начать практику с ИИ
          </RouterLink>
          <RouterLink to="/login"
            class="border border-gray-200 dark:border-neutral-700 bg-white dark:bg-neutral-900
                   px-7 py-3.5 rounded-full font-medium transition">
            У меня есть аккаунт
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- Два направления -->
    <section class="pb-4">
      <div class="max-w-5xl mx-auto px-4 grid md:grid-cols-2 gap-4">
        <div v-for="p in products" :key="p.tag"
          class="bg-white dark:bg-neutral-900 rounded-3xl border border-gray-100
                 dark:border-neutral-800 p-6 sm:p-8">
          <div class="flex items-center gap-2">
            <span class="text-2xl">{{ p.icon }}</span>
            <span class="px-2.5 py-0.5 rounded-full bg-red-50 dark:bg-neutral-800
                         text-red-500 text-xs font-medium">{{ p.tag }}</span>
          </div>
          <h3 class="mt-3 text-xl font-bold">{{ p.title }}</h3>
          <p class="mt-2 text-sm text-gray-500 dark:text-gray-400 leading-6">{{ p.text }}</p>
          <ul class="mt-4 space-y-2">
            <li v-for="pt in p.points" :key="pt" class="flex items-start gap-2 text-sm">
              <span class="text-red-500 mt-0.5">✓</span>
              <span class="text-gray-600 dark:text-gray-300">{{ pt }}</span>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Как работает AI практика -->
    <section class="py-16">
      <div class="max-w-5xl mx-auto px-4">
        <h2 class="text-2xl sm:text-3xl font-bold text-center">Как работает AI практика</h2>
        <p class="text-gray-500 dark:text-gray-400 mt-2 text-center text-sm">
          Три шага — и ты уже говоришь
        </p>
        <div class="grid sm:grid-cols-3 gap-4 mt-10">
          <div v-for="s in aiSteps" :key="s.title"
            class="bg-white dark:bg-neutral-900 rounded-2xl border border-gray-100
                   dark:border-neutral-800 p-6 text-center">
            <div class="text-3xl">{{ s.icon }}</div>
            <h3 class="font-semibold mt-3">{{ s.title }}</h3>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-2 leading-6">{{ s.text }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- PWA -->
    <section class="pb-16">
      <div class="max-w-5xl mx-auto px-4">
        <div class="bg-gray-900 dark:bg-neutral-900 rounded-3xl text-white px-6 sm:px-10 py-10
                    flex flex-col sm:flex-row items-center gap-6 text-center sm:text-left">
          <div class="text-5xl">📱</div>
          <div class="flex-1">
            <h2 class="text-xl sm:text-2xl font-bold">Установи как приложение</h2>
            <p class="mt-2 text-white/70 text-sm max-w-xl">
              ТІЛДЕС — это PWA. Открой сайт на телефоне и нажми «Добавить на главный экран» —
              работает как обычное приложение, с микрофоном и офлайн-кэшем.
            </p>
          </div>
          <RouterLink to="/register"
            class="bg-red-500 hover:bg-red-600 px-6 py-3 rounded-full font-medium transition shrink-0">
            Попробовать
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-white dark:bg-neutral-900 border-t border-gray-100 dark:border-neutral-800">
      <div class="max-w-5xl mx-auto px-4 py-8">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-full bg-red-500 text-white flex items-center justify-center text-sm">T</div>
          <span class="font-medium">ТІЛДЕС</span>
        </div>
        <p class="text-gray-500 dark:text-gray-400 text-sm mt-3">
          Изучение казахского: разговор с ИИ и обучение с преподавателями.
        </p>
        <p class="text-xs text-gray-400 mt-3">© 2026 ТІЛДЕС</p>
      </div>
    </footer>
  </div>
</template>
