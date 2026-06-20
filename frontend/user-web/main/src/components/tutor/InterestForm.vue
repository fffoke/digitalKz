<script setup>
import { reactive, computed, onMounted } from 'vue'

// Форма интересов. Эмитит submit с { motivation, interests, contexts, case_text }.
// initial — для редактирования уже сохранённых ответов (предзаполнение).
const props = defineProps({
  loading: { type: Boolean, default: false },
  initial: { type: Object, default: null },
  submitLabel: { type: String, default: 'Создать задания' },
})
const emit = defineEmits(['submit'])

const MOTIVATIONS = [
  { key: 'work', label: 'для работы с клиентами' },
  { key: 'move', label: 'для жизни после переезда' },
  { key: 'family', label: 'чтобы говорить с родными' },
  { key: 'culture', label: 'чтобы понимать культуру' },
  { key: 'travel', label: 'для поездок по Казахстану' },
  { key: 'study', label: 'для учёбы и экзаменов' },
]
const INTERESTS = [
  'футбол и спорт', 'кино и сериалы', 'IT и стартапы', 'еда и кафе',
  'бизнес и переговоры', 'музыка', 'история Казахстана', 'природа и путешествия',
  'игры', 'мода', 'наука', 'авто',
]
const CONTEXTS = [
  { key: 'work', label: 'на работе и встречах' },
  { key: 'bazaar', label: 'в магазине или на базаре' },
  { key: 'family', label: 'дома и в семье' },
  { key: 'gov', label: 'в ЦОНе и госуслугах' },
  { key: 'travel', label: 'в поездках по стране' },
  { key: 'friends', label: 'с друзьями и соседями' },
]

const motivationByKey = Object.fromEntries(MOTIVATIONS.map((item) => [item.key, item.label]))
const contextByKey = Object.fromEntries(CONTEXTS.map((item) => [item.key, item.label]))

const form = reactive({
  motivation: '',
  interests: [],
  contexts: [],
  case_text: '',
})

const custom = reactive({
  motivation: '',
  interest: '',
  context: '',
})

onMounted(() => {
  if (props.initial) {
    form.motivation = motivationByKey[props.initial.motivation] || props.initial.motivation || ''
    form.interests = [...(props.initial.interests || [])]
    form.contexts = (props.initial.contexts || []).map((item) => contextByKey[item] || item)
  }
})

const toggle = (arr, v) => {
  const i = arr.indexOf(v)
  if (i === -1) arr.push(v)
  else arr.splice(i, 1)
}

const clean = (value) => value.trim().replace(/\s+/g, ' ')

const addUnique = (arr, value) => {
  const text = clean(value)
  if (!text || arr.includes(text)) return false
  arr.push(text)
  return true
}

const addMotivation = () => {
  const text = clean(custom.motivation)
  if (!text) return
  form.motivation = text
  custom.motivation = ''
}

const addInterest = () => {
  if (addUnique(form.interests, custom.interest)) custom.interest = ''
}

const addContext = () => {
  if (addUnique(form.contexts, custom.context)) custom.context = ''
}

const valid = computed(() =>
  form.motivation && form.interests.length > 0 && form.contexts.length > 0)

const submit = () => {
  if (!valid.value) return
  emit('submit', { ...form, case_text: '' })
}
</script>

<template>
  <div class="space-y-7">
    <!-- 1. Зачем -->
    <section>
      <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">
        1. Зачем учишь казахский?
      </h3>
      <p class="mb-3 text-xs text-gray-500 dark:text-gray-400">
        Формат: “для чего” + “где пригодится”, например: для работы с клиентами в Алматы.
      </p>
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
        <button
          v-for="m in MOTIVATIONS" :key="m.key" type="button"
          class="flex items-center gap-2 px-3 py-2.5 rounded-xl border text-sm transition"
          :class="form.motivation === m.label
            ? 'border-red-500 bg-red-50 dark:bg-neutral-800 text-red-600 font-medium'
            : 'border-gray-200 dark:border-neutral-700 text-gray-600 dark:text-gray-300'"
          @click="form.motivation = m.label"
        >
          {{ m.label }}
        </button>
      </div>
      <div class="mt-3 flex gap-2">
        <input
          v-model="custom.motivation"
          type="text"
          placeholder="Например: для общения с родителями учеников"
          class="min-w-0 flex-1 rounded-xl border border-gray-200 dark:border-neutral-700
                 bg-transparent px-3 py-2.5 text-sm text-gray-800 dark:text-gray-100
                 placeholder:text-gray-400 focus:border-red-400 focus:outline-none"
          @keydown.enter.prevent="addMotivation"
        >
        <button
          type="button"
          class="h-11 w-11 shrink-0 rounded-xl bg-red-500 text-xl leading-none text-white
                 hover:bg-red-600 disabled:opacity-40"
          :disabled="!clean(custom.motivation)"
          aria-label="Добавить цель"
          @click="addMotivation"
        >
          +
        </button>
      </div>
      <p v-if="form.motivation" class="mt-2 text-xs text-red-500">
        Выбрано: {{ form.motivation }}
      </p>
    </section>

    <!-- 2. Интересы -->
    <section>
      <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">
        2. Что тебе интересно? <span class="text-gray-400 font-normal">(несколько)</span>
      </h3>
      <p class="mb-3 text-xs text-gray-500 dark:text-gray-400">
        Формат: тема + уточнение, например: футбол и разговоры о матчах.
      </p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="t in INTERESTS" :key="t" type="button"
          class="px-3 py-1.5 rounded-full border text-sm transition"
          :class="form.interests.includes(t)
            ? 'border-red-500 bg-red-500 text-white'
            : 'border-gray-200 dark:border-neutral-700 text-gray-600 dark:text-gray-300'"
          @click="toggle(form.interests, t)"
        >
          {{ t }}
        </button>
      </div>
      <div class="mt-3 flex gap-2">
        <input
          v-model="custom.interest"
          type="text"
          placeholder="Например: дизайн интерфейсов и приложения"
          class="min-w-0 flex-1 rounded-xl border border-gray-200 dark:border-neutral-700
                 bg-transparent px-3 py-2.5 text-sm text-gray-800 dark:text-gray-100
                 placeholder:text-gray-400 focus:border-red-400 focus:outline-none"
          @keydown.enter.prevent="addInterest"
        >
        <button
          type="button"
          class="h-11 w-11 shrink-0 rounded-xl bg-red-500 text-xl leading-none text-white
                 hover:bg-red-600 disabled:opacity-40"
          :disabled="!clean(custom.interest)"
          aria-label="Добавить интерес"
          @click="addInterest"
        >
          +
        </button>
      </div>
    </section>

    <!-- 3. Где пригодится -->
    <section>
      <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">
        3. Где казахский пригодится? <span class="text-gray-400 font-normal">(несколько)</span>
      </h3>
      <p class="mb-3 text-xs text-gray-500 dark:text-gray-400">
        Формат: место или ситуация + действие, например: в поликлинике объяснить симптомы.
      </p>
      <div class="grid grid-cols-2 gap-2">
        <button
          v-for="c in CONTEXTS" :key="c.key" type="button"
          class="px-3 py-2.5 rounded-xl border text-sm transition"
          :class="form.contexts.includes(c.label)
            ? 'border-red-500 bg-red-50 dark:bg-neutral-800 text-red-600 font-medium'
            : 'border-gray-200 dark:border-neutral-700 text-gray-600 dark:text-gray-300'"
          @click="toggle(form.contexts, c.label)"
        >
          {{ c.label }}
        </button>
      </div>
      <div class="mt-3 flex gap-2">
        <input
          v-model="custom.context"
          type="text"
          placeholder="Например: на работе вести короткие созвоны"
          class="min-w-0 flex-1 rounded-xl border border-gray-200 dark:border-neutral-700
                 bg-transparent px-3 py-2.5 text-sm text-gray-800 dark:text-gray-100
                 placeholder:text-gray-400 focus:border-red-400 focus:outline-none"
          @keydown.enter.prevent="addContext"
        >
        <button
          type="button"
          class="h-11 w-11 shrink-0 rounded-xl bg-red-500 text-xl leading-none text-white
                 hover:bg-red-600 disabled:opacity-40"
          :disabled="!clean(custom.context)"
          aria-label="Добавить ситуацию"
          @click="addContext"
        >
          +
        </button>
      </div>
    </section>

    <button
      class="w-full bg-red-500 hover:bg-red-600 disabled:opacity-40 text-white
             font-semibold rounded-xl py-3 text-sm transition"
      :disabled="!valid || loading"
      @click="submit"
    >
      {{ loading ? 'Готовим задания…' : submitLabel }}
    </button>
  </div>
</template>
