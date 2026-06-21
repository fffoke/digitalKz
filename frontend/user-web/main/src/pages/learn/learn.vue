<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import AppLayout from '@/components/layout/AppLayout.vue'
import GroupChat from '@/components/learning/GroupChat.vue'
import { getRoleStatus, submitVerification, applyTeacher } from '@/services/onboarding'
import {
  completeLesson,
  createGroup,
  getEntranceExam,
  getLearningOverview,
  leaveGroup,
  gradeHomework,
  joinGroup,
  joinGroupByCode,
  rateLesson,
  scheduleLesson,
  startLesson,
  submitEntranceTest,
  submitHomework,
  submitLevelExam,
} from '@/services/learning'

const router = useRouter()

const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const mode = ref('choose')
const status = ref(null)
const overview = ref(null)

const iin = ref('')
const teacherForm = ref({ education: '', experience: '', kazakh_level: 'B2' })
const groupTab = ref('chat')
const testAnswers = ref({})
const examQuestions = ref([])
const listeningAnswers = ref({ l1: '', l2: '', l3: '' })
const readingText = ref('')
const groupForm = ref({ name: '', schedule: 'three_week' })
const inviteCode = ref('')
const lessonStarts = ref('')
const planDrafts = ref({})   // group_id -> datetime для планирования урока
const homeworkDrafts = ref({})
const gradeDrafts = ref({})
const ratingDrafts = ref({})
const levelExamAnswers = ref({})
const levelReadingText = ref('')

const LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1']
const schedules = {
  once_week: '1 раз в неделю',
  three_week: '3 раза в неделю',
  intensive: 'Интенсив',
}
const lessonStatus = {
  scheduled: 'Запланирован',
  open: 'Чат и Meet открыты',
  completed: 'Проведён',
  cancelled: 'Отменён',
}
const homeworkStatus = {
  assigned: 'Выдано',
  submitted: 'Отправлено',
  graded: 'Проверено',
}

const role = computed(() => overview.value?.role || status.value?.role)
const isStudent = computed(() => role.value === 'student')
const isTeacher = computed(() => role.value === 'teacher')
const currentGroup = computed(() => overview.value?.current_group)
const needsTest = computed(() => overview.value?.needs_entrance_test)

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    status.value = (await getRoleStatus()).data
    if (status.value.role === 'student' || status.value.role === 'teacher') {
      overview.value = (await getLearningOverview()).data
      if (overview.value?.needs_entrance_test) {
        examQuestions.value = (await getEntranceExam()).data.questions || []
      }
    }
  } catch (e) {
    console.log(e.response)
    error.value = 'Не удалось загрузить обучение'
  } finally {
    loading.value = false
  }
}

const becomeStudent = async () => {
  if (iin.value.trim().length !== 12) {
    error.value = 'ИИН должен быть из 12 цифр'
    return
  }
  submitting.value = true
  error.value = ''
  try {
    await submitVerification(iin.value.trim(), null)
    mode.value = 'choose'
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось выдать роль ученика'
  } finally {
    submitting.value = false
  }
}

const sendTeacher = async () => {
  if (!teacherForm.value.education.trim() || !teacherForm.value.experience.trim()) {
    error.value = 'Заполните образование и опыт'
    return
  }
  submitting.value = true
  error.value = ''
  try {
    await applyTeacher(teacherForm.value)
    mode.value = 'choose'
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось отправить анкету'
  } finally {
    submitting.value = false
  }
}

const answerValue = (i) => testAnswers.value[`q${i}`] || ''
const setAnswer = (i, value) => { testAnswers.value[`q${i}`] = value }

const finishEntrance = async () => {
  submitting.value = true
  error.value = ''
  try {
    await submitEntranceTest({
      answers: testAnswers.value,
      listening_answers: listeningAnswers.value,
      reading_text: readingText.value,
    })
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось завершить тест'
  } finally {
    submitting.value = false
  }
}

const finishLevelExam = async () => {
  submitting.value = true
  error.value = ''
  try {
    await submitLevelExam({
      answers: levelExamAnswers.value,
      listening_answers: {},
      reading_text: levelReadingText.value,
    })
    levelExamAnswers.value = {}
    levelReadingText.value = ''
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось сдать экзамен'
  } finally {
    submitting.value = false
  }
}

const createOwnGroup = async () => {
  submitting.value = true
  error.value = ''
  try {
    await createGroup({
      name: groupForm.value.name || null,
      schedule: groupForm.value.schedule,
    })
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось создать группу'
  } finally {
    submitting.value = false
  }
}

const join = async (group) => {
  submitting.value = true
  error.value = ''
  try {
    await joinGroup(group.id)
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось вступить в группу'
  } finally {
    submitting.value = false
  }
}

const leaveCurrentGroup = async () => {
  if (!currentGroup.value) return
  if (!confirm('Покинуть группу? Доступ к чату пропадёт.')) return
  submitting.value = true
  error.value = ''
  try {
    await leaveGroup(currentGroup.value.id)
    groupTab.value = 'chat'
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось покинуть группу'
  } finally {
    submitting.value = false
  }
}

const goExam = () => router.push({ name: 'level-exam' })

const goChat = () => router.push({ name: 'group-chat', params: { groupId: currentGroup.value.id } })
const goChatFor = (groupId) => router.push({ name: 'group-chat', params: { groupId } })
const goHomework = () => router.push({ name: 'homework' })

const lessonTime = (lesson) => {
  const opts = { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }
  const start = new Date(lesson.starts_at).toLocaleString('ru', opts)
  if (!lesson.ends_at) return start
  const end = new Date(lesson.ends_at).toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' })
  return `${start} – ${end}`
}

const joinLesson = (lesson) => {
  if (lesson.meet_link) window.open(lesson.meet_link, '_blank')
}

const startGroupLesson = async (group) => {
  submitting.value = true
  error.value = ''
  try {
    const { data } = await startLesson(group.id)
    if (data.meet_link) window.open(data.meet_link, '_blank')
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось начать урок'
  } finally {
    submitting.value = false
  }
}

const joinByInvite = async () => {
  if (!inviteCode.value.trim()) return
  submitting.value = true
  error.value = ''
  try {
    await joinGroupByCode(inviteCode.value.trim())
    inviteCode.value = ''
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось вступить по ссылке'
  } finally {
    submitting.value = false
  }
}

const planLesson = async (group) => {
  const when = planDrafts.value[group.id]
  if (!when) {
    alert('Сначала выберите дату и время урока для этой группы')
    return
  }
  submitting.value = true
  error.value = ''
  try {
    await scheduleLesson(group.id, new Date(when).toISOString())
    planDrafts.value[group.id] = ''
    await load()
  } catch (e) {
    alert(e.response?.data?.detail || 'Не удалось запланировать урок')
  } finally {
    submitting.value = false
  }
}

const finishLesson = async (lesson) => {
  submitting.value = true
  error.value = ''
  try {
    await completeLesson(lesson.id)
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось завершить урок'
  } finally {
    submitting.value = false
  }
}

const sendHomework = async (homework) => {
  const text = homeworkDrafts.value[homework.id]?.trim()
  if (!text) return
  submitting.value = true
  error.value = ''
  try {
    await submitHomework(homework.id, text)
    homeworkDrafts.value[homework.id] = ''
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось отправить ДЗ'
  } finally {
    submitting.value = false
  }
}

const sendGrade = async (homework) => {
  const draft = gradeDrafts.value[homework.id] || { grade: 90, feedback: '' }
  submitting.value = true
  error.value = ''
  try {
    await gradeHomework(homework.id, draft)
    gradeDrafts.value[homework.id] = { grade: 90, feedback: '' }
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось проверить ДЗ'
  } finally {
    submitting.value = false
  }
}

const ensureGradeDraft = (homework) => {
  if (!gradeDrafts.value[homework.id]) {
    gradeDrafts.value[homework.id] = { grade: 90, feedback: '' }
  }
  return gradeDrafts.value[homework.id]
}

const sendRating = async (lesson) => {
  const draft = ratingDrafts.value[lesson.id] || { score: 5, review: '', anonymous: false }
  submitting.value = true
  error.value = ''
  try {
    await rateLesson(lesson.id, draft)
    ratingDrafts.value[lesson.id] = { score: 5, review: '', anonymous: false }
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось отправить оценку'
  } finally {
    submitting.value = false
  }
}

const ensureRatingDraft = (lesson) => {
  if (!ratingDrafts.value[lesson.id]) {
    ratingDrafts.value[lesson.id] = { score: 5, review: '', anonymous: false }
  }
  return ratingDrafts.value[lesson.id]
}

onMounted(load)
</script>

<template>
  <AppLayout title="Обучение">
    <div v-if="loading" class="py-24 text-center text-gray-400">Загрузка…</div>

    <div v-else class="px-3 sm:px-4 py-4 space-y-4">
      <p v-if="error" class="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-600">
        {{ error }}
      </p>

      <template v-if="!isStudent && !isTeacher">
        <div v-if="status?.teacher_application_status === 'pending'"
             class="rounded-2xl border border-amber-200 bg-amber-50 p-5 text-center dark:border-neutral-800 dark:bg-neutral-900">
          <h2 class="font-bold text-gray-900 dark:text-white">Анкета преподавателя на рассмотрении</h2>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Центр свяжется с вами для онлайн-созвона и проверки навыков.
          </p>
        </div>

        <template v-else-if="mode === 'choose'">
          <div class="text-center pt-2">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white">Выберите путь</h2>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Ученики получают доступ сразу, преподаватели проходят модерацию.
            </p>
          </div>

          <div class="grid gap-3 sm:grid-cols-2">
            <button
              class="rounded-2xl border border-gray-100 bg-white p-5 text-left shadow-sm transition hover:border-red-200 dark:border-neutral-800 dark:bg-neutral-900"
              @click="mode = 'student'; error = ''"
            >
              <img src="/uchenik.svg" alt="Ученик" class="h-24 w-24 object-contain" />
              <h3 class="mt-3 font-bold text-gray-900 dark:text-white">Ученик</h3>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Введите ИИН и сразу переходите к вступительному тесту.
              </p>
            </button>

            <button
              class="rounded-2xl border border-gray-100 bg-white p-5 text-left shadow-sm transition hover:border-red-200 dark:border-neutral-800 dark:bg-neutral-900"
              @click="mode = 'teacher'; error = ''"
            >
              <img src="/Prepod.svg" alt="Преподаватель" class="h-24 w-24 object-contain" />
              <h3 class="mt-3 font-bold text-gray-900 dark:text-white">Преподаватель</h3>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Заполните анкету, затем центр проведёт онлайн-созвон.
              </p>
            </button>
          </div>
        </template>

        <div v-else-if="mode === 'student'"
             class="rounded-2xl border border-gray-100 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900">
          <h3 class="font-bold text-gray-900 dark:text-white">Стать учеником</h3>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Модерации для учеников нет. ИИН нужен только как шаг идентификации в прототипе.
          </p>
          <input
            v-model="iin"
            inputmode="numeric"
            maxlength="12"
            placeholder="12 цифр ИИН"
            class="mt-4 w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-3 text-sm focus:border-red-400 focus:outline-none dark:border-neutral-700 dark:bg-neutral-800 dark:text-white"
          >
          <div class="mt-4 flex gap-2">
            <button class="flex-1 rounded-xl bg-gray-100 py-3 text-sm font-medium dark:bg-neutral-800 dark:text-gray-200"
                    @click="mode = 'choose'">Назад</button>
            <button class="flex-1 rounded-xl bg-red-500 py-3 text-sm font-semibold text-white disabled:opacity-50"
                    :disabled="submitting" @click="becomeStudent">
              {{ submitting ? 'Сохраняем…' : 'Начать обучение' }}
            </button>
          </div>
        </div>

        <div v-else-if="mode === 'teacher'"
             class="rounded-2xl border border-gray-100 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900">
          <h3 class="font-bold text-gray-900 dark:text-white">Анкета преподавателя</h3>
          <div class="mt-4 space-y-3">
            <textarea v-model="teacherForm.education" rows="2" placeholder="Образование"
              class="w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-3 text-sm focus:border-red-400 focus:outline-none dark:border-neutral-700 dark:bg-neutral-800 dark:text-white" />
            <textarea v-model="teacherForm.experience" rows="2" placeholder="Опыт преподавания"
              class="w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-3 text-sm focus:border-red-400 focus:outline-none dark:border-neutral-700 dark:bg-neutral-800 dark:text-white" />
            <select v-model="teacherForm.kazakh_level"
              class="w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-3 text-sm focus:border-red-400 focus:outline-none dark:border-neutral-700 dark:bg-neutral-800 dark:text-white">
              <option v-for="level in LEVELS" :key="level" :value="level">{{ level }}</option>
            </select>
          </div>
          <div class="mt-4 flex gap-2">
            <button class="flex-1 rounded-xl bg-gray-100 py-3 text-sm font-medium dark:bg-neutral-800 dark:text-gray-200"
                    @click="mode = 'choose'">Назад</button>
            <button class="flex-1 rounded-xl bg-red-500 py-3 text-sm font-semibold text-white disabled:opacity-50"
                    :disabled="submitting" @click="sendTeacher">
              {{ submitting ? 'Отправляем…' : 'Отправить анкету' }}
            </button>
          </div>
        </div>
      </template>

      <template v-else>
        <div class="rounded-2xl bg-gradient-to-br from-red-500 to-red-600 p-5 text-white">
          <p class="text-sm opacity-90">{{ isTeacher ? 'Преподавательская биржа' : 'Основное обучение' }}</p>
          <h2 class="mt-1 text-2xl font-bold">
            {{ isTeacher ? 'Группы и уроки' : `Уровень ${overview?.level || 'не определён'}` }}
          </h2>
          <p class="mt-1 text-sm opacity-85">
            Ранг: {{ overview?.rank || 'Бастауыш' }}
          </p>
        </div>

        <section v-if="needsTest" class="rounded-2xl border border-gray-100 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900">
          <h3 class="font-bold text-gray-900 dark:text-white">Вступительный тест</h3>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Ответьте на вопросы — система определит ваш уровень (A1–C1).
          </p>

          <div class="mt-4 space-y-4">
            <div v-for="(q, idx) in examQuestions" :key="idx" v-show="q.type === 'choice'">
              <p class="text-sm font-medium text-gray-800 dark:text-gray-100">{{ idx + 1 }}. {{ q.text }}</p>
              <div class="mt-2 flex flex-wrap gap-2">
                <button
                  v-for="opt in q.options" :key="opt"
                  class="rounded-lg border px-3 py-2 text-sm transition"
                  :class="answerValue(idx) === opt
                    ? 'border-red-500 bg-red-50 text-red-600'
                    : 'border-gray-200 text-gray-600 dark:border-neutral-700 dark:text-gray-300'"
                  @click="setAnswer(idx, opt)"
                >
                  {{ opt }}
                </button>
              </div>
            </div>
            <p v-if="!examQuestions.length" class="text-sm text-gray-400">
              Вопросы ещё не добавлены администратором.
            </p>
          </div>
          <div class="mt-4 space-y-2">
            <input v-model="listeningAnswers.l1" placeholder="Ответ на голосовой вопрос 1"
              class="w-full rounded-xl border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm dark:border-neutral-700 dark:bg-neutral-800 dark:text-white">
            <input v-model="listeningAnswers.l2" placeholder="Ответ на голосовой вопрос 2"
              class="w-full rounded-xl border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm dark:border-neutral-700 dark:bg-neutral-800 dark:text-white">
            <input v-model="listeningAnswers.l3" placeholder="Ответ на голосовой вопрос 3"
              class="w-full rounded-xl border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm dark:border-neutral-700 dark:bg-neutral-800 dark:text-white">
            <textarea v-model="readingText" rows="3" placeholder="Текст, который ученик прочитал голосом"
              class="w-full rounded-xl border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm dark:border-neutral-700 dark:bg-neutral-800 dark:text-white" />
          </div>
          <button class="mt-4 w-full rounded-xl bg-red-500 py-3 text-sm font-semibold text-white disabled:opacity-50"
                  :disabled="submitting" @click="finishEntrance">
            Завершить тест
          </button>
        </section>

        <template v-else-if="isStudent">
          <template v-if="currentGroup">
            <!-- шапка группы + покинуть -->
            <section class="rounded-2xl border border-gray-100 bg-white p-4 dark:border-neutral-800 dark:bg-neutral-900">
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <h3 class="font-bold text-gray-900 dark:text-white truncate">{{ currentGroup.name }}</h3>
                  <p class="mt-0.5 text-xs text-gray-500 dark:text-gray-400">
                    {{ currentGroup.level }} · {{ schedules[currentGroup.schedule] }} · {{ currentGroup.members_count }}/5
                  </p>
                </div>
                <button
                  class="shrink-0 rounded-xl bg-gray-100 px-3 py-2 text-xs font-medium text-red-500
                         hover:bg-red-50 dark:bg-neutral-800 dark:hover:bg-neutral-700 disabled:opacity-50"
                  :disabled="submitting" @click="leaveCurrentGroup"
                >
                  Покинуть
                </button>
              </div>
              <p class="mt-2 rounded-lg bg-gray-50 px-2.5 py-1.5 text-[11px] text-gray-500 dark:bg-neutral-800 dark:text-gray-300">
                Код для друзей: {{ currentGroup.invite_code }}
              </p>
            </section>

            <!-- основные кнопки: Чат / ДЗ / Экзамен -->
            <div class="grid grid-cols-3 gap-2">
              <button
                class="rounded-2xl bg-red-500 hover:bg-red-600 text-white py-4 font-semibold text-xs transition flex flex-col items-center gap-1"
                @click="goChat">
                <span class="text-2xl">💬</span>
                Чат
              </button>
              <button
                class="rounded-2xl bg-blue-600 hover:bg-blue-700 text-white py-4 font-semibold text-xs transition flex flex-col items-center gap-1"
                @click="goHomework">
                <span class="text-2xl">📒</span>
                ДЗ
              </button>
              <button
                class="rounded-2xl bg-gray-900 hover:bg-gray-800 text-white py-4 font-semibold text-xs transition flex flex-col items-center gap-1"
                @click="goExam">
                <span class="text-2xl">📝</span>
                Экзамен
              </button>
            </div>

            <!-- уроки (с оценкой) -->
            <section v-if="overview?.lessons?.length" class="rounded-2xl border border-gray-100 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900">
              <h3 class="font-bold text-gray-900 dark:text-white">Уроки</h3>
              <div class="mt-3 space-y-2">
                <div v-for="lesson in overview.lessons" :key="lesson.id"
                     class="rounded-xl border p-3"
                     :class="['open','scheduled'].includes(lesson.status) ? 'border-green-200 bg-green-50 dark:border-green-900/40 dark:bg-green-900/10' : 'border-gray-100 dark:border-neutral-800'">
                  <div class="flex items-center justify-between gap-3">
                    <div class="min-w-0">
                      <p class="text-sm font-medium text-gray-800 dark:text-gray-100">{{ lessonStatus[lesson.status] }}</p>
                      <p class="text-xs text-gray-500 dark:text-gray-400">{{ lessonTime(lesson) }}</p>
                      <p v-if="lesson.teacher_name" class="text-xs text-gray-400">Преподаватель: {{ lesson.teacher_name }}</p>
                    </div>
                    <button v-if="lesson.meet_link && lesson.status !== 'completed'"
                      class="shrink-0 rounded-xl bg-blue-600 hover:bg-blue-700 px-4 py-2 text-xs font-semibold text-white"
                      @click="joinLesson(lesson)">
                      Подключиться
                    </button>
                  </div>
                  <!-- оценка завершённого урока -->
                  <template v-if="lesson.status === 'completed'">
                    <!-- уже оценил → показываем оценку, кнопки нет -->
                    <div v-if="lesson.rated" class="mt-3 text-sm text-gray-600 dark:text-gray-300">
                      ⭐ Ваша оценка: <span class="font-semibold text-gray-900 dark:text-white">{{ lesson.my_score }}/5</span>
                      <span v-if="lesson.my_review"> — «{{ lesson.my_review }}»</span>
                    </div>
                    <!-- ещё не оценил → форма -->
                    <div v-else class="mt-3 grid gap-2 sm:grid-cols-[80px_1fr_auto]">
                      <select v-model="ensureRatingDraft(lesson).score"
                        class="rounded-xl border border-gray-200 bg-white px-2 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900 dark:text-white">
                        <option v-for="score in [5,4,3,2,1]" :key="score" :value="score">{{ score }}</option>
                      </select>
                      <input v-model="ensureRatingDraft(lesson).review" placeholder="Отзыв об уроке"
                        class="rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900 dark:text-white">
                      <button class="rounded-xl bg-red-500 px-3 py-2 text-sm font-semibold text-white"
                              @click="sendRating(lesson)">Оценить</button>
                    </div>
                  </template>
                </div>
              </div>
            </section>

            <!-- карта прогресса -->
            <section class="rounded-2xl border border-gray-100 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900">
              <h3 class="font-bold text-gray-900 dark:text-white">Карта прогресса</h3>
              <div v-if="overview?.progress?.length" class="mt-4 grid grid-cols-3 gap-2">
                <div v-for="stage in overview.progress" :key="`${stage.section}-${stage.stage}`"
                     class="rounded-xl border p-3 text-xs"
                     :class="stage.status === 'done' ? 'border-green-200 bg-green-50 text-green-700' : stage.status === 'current' ? 'border-red-200 bg-red-50 text-red-600' : 'border-gray-200 text-gray-400 dark:border-neutral-700'">
                  {{ stage.title }}
                </div>
              </div>
              <p v-else class="mt-3 text-sm text-gray-400">План появится после первого урока.</p>
            </section>
          </template>

          <section v-else class="space-y-3">
            <div class="rounded-2xl border border-gray-100 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900">
              <h3 class="font-bold text-gray-900 dark:text-white">Выбор группы</h3>
              <div class="mt-3 flex gap-2">
                <input v-model="inviteCode" placeholder="Код приглашения"
                  class="min-w-0 flex-1 rounded-xl border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm dark:border-neutral-700 dark:bg-neutral-800 dark:text-white">
                <button class="rounded-xl bg-red-500 px-4 text-sm font-semibold text-white"
                        @click="joinByInvite">Войти</button>
              </div>
            </div>

            <div class="rounded-2xl border border-gray-100 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900">
              <h3 class="font-bold text-gray-900 dark:text-white">Создать свою группу</h3>
              <div class="mt-3 grid gap-2 sm:grid-cols-2">
                <input v-model="groupForm.name" placeholder="Название группы"
                  class="rounded-xl border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm dark:border-neutral-700 dark:bg-neutral-800 dark:text-white">
                <select v-model="groupForm.schedule"
                  class="rounded-xl border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm dark:border-neutral-700 dark:bg-neutral-800 dark:text-white">
                  <option v-for="(label, key) in schedules" :key="key" :value="key">{{ label }}</option>
                </select>
              </div>
              <button class="mt-3 w-full rounded-xl bg-red-500 py-3 text-sm font-semibold text-white"
                      @click="createOwnGroup">Создать и получить ссылку</button>
            </div>

            <div v-for="group in overview?.available_groups" :key="group.id"
                 class="rounded-2xl border border-gray-100 bg-white p-4 dark:border-neutral-800 dark:bg-neutral-900">
              <div class="flex items-center justify-between gap-3">
                <div>
                  <h4 class="font-semibold text-gray-900 dark:text-white">{{ group.name }}</h4>
                  <p class="text-sm text-gray-500">{{ group.level }} · {{ schedules[group.schedule] }} · {{ group.members_count }}/5</p>
                </div>
                <button class="rounded-xl bg-red-500 px-4 py-2 text-sm font-semibold text-white"
                        @click="join(group)">Войти</button>
              </div>
            </div>
          </section>
        </template>

        <!-- мои группы (преподаватель) -->
        <section v-if="isTeacher && overview?.teacher_groups?.length"
                 class="rounded-2xl border border-gray-100 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900">
          <div class="flex items-center justify-between">
            <h3 class="font-bold text-gray-900 dark:text-white">Мои группы</h3>
            <button class="rounded-xl bg-blue-600 hover:bg-blue-700 px-3 py-1.5 text-xs font-semibold text-white"
                    @click="goHomework">📒 Проверить ДЗ</button>
          </div>
          <div class="mt-3 space-y-2">
            <div v-for="group in overview.teacher_groups" :key="group.id"
                 class="rounded-xl border border-gray-100 p-3 dark:border-neutral-800">
              <div class="flex items-center justify-between gap-2">
                <div class="min-w-0">
                  <p class="font-semibold text-gray-900 dark:text-white truncate">{{ group.name }}</p>
                  <p class="text-xs text-gray-500">{{ group.level }} · {{ group.members_count }}/5 учеников</p>
                </div>
                <div class="flex shrink-0 gap-2">
                  <button class="rounded-xl bg-red-500 hover:bg-red-600 px-3 py-2 text-xs font-semibold text-white"
                          @click="goChatFor(group.id)">💬 Чат</button>
                  <button class="rounded-xl bg-blue-600 hover:bg-blue-700 px-3 py-2 text-xs font-semibold text-white disabled:opacity-50"
                          :disabled="submitting" @click="startGroupLesson(group)">📹 Урок</button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section v-if="isTeacher" class="rounded-2xl border border-gray-100 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900">
          <h3 class="font-bold text-gray-900 dark:text-white">Группы без преподавателя</h3>
          <p class="mt-0.5 text-xs text-gray-400">Начните урок сейчас или запланируйте на дату</p>
          <div class="mt-3 space-y-2">
            <div v-for="group in overview?.open_teacher_groups" :key="group.id"
                 class="rounded-xl border border-gray-100 p-3 dark:border-neutral-800 space-y-2">
              <div class="flex items-center justify-between gap-2">
                <div class="min-w-0">
                  <p class="font-semibold text-gray-900 dark:text-white truncate">{{ group.name }}</p>
                  <p class="text-xs text-gray-500">{{ group.level }} · секция {{ group.current_section }}, этап {{ group.current_stage }} · {{ group.members_count }}/5</p>
                </div>
                <button class="shrink-0 rounded-xl bg-blue-600 hover:bg-blue-700 px-3 py-2 text-xs font-semibold text-white disabled:opacity-50"
                        :disabled="submitting" @click="startGroupLesson(group)">📹 Начать сейчас</button>
              </div>
              <div class="flex gap-2">
                <input v-model="planDrafts[group.id]" type="datetime-local"
                  class="min-w-0 flex-1 rounded-xl border border-gray-200 bg-gray-50 px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-800 dark:text-white">
                <button class="shrink-0 rounded-xl bg-gray-100 px-3 py-2 text-xs font-semibold text-gray-700 dark:bg-neutral-700 dark:text-gray-200 disabled:opacity-50"
                        :disabled="submitting" @click="planLesson(group)">Запланировать</button>
              </div>
            </div>
            <p v-if="!overview?.open_teacher_groups?.length" class="py-4 text-center text-sm text-gray-400">
              Пока нет групп, готовых к уроку.
            </p>
          </div>
        </section>

        <!-- уроки преподавателя (вести/завершать) -->
        <section v-if="isTeacher && overview?.lessons?.length" class="rounded-2xl border border-gray-100 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900">
          <h3 class="font-bold text-gray-900 dark:text-white">Мои уроки</h3>
          <div class="mt-3 space-y-3">
            <div v-for="lesson in overview.lessons" :key="lesson.id" class="rounded-xl bg-gray-50 p-3 dark:bg-neutral-800">
              <p class="font-semibold text-gray-900 dark:text-white">{{ lessonTime(lesson) }}</p>
              <p class="text-xs text-gray-500">{{ lessonStatus[lesson.status] }}</p>
              <a v-if="lesson.meet_link" :href="lesson.meet_link" target="_blank"
                 class="mt-2 inline-flex rounded-full bg-white px-3 py-1.5 text-xs font-semibold text-red-600 dark:bg-neutral-900">
                Открыть видеозвонок
              </a>
              <button v-if="lesson.status !== 'completed'"
                      class="ml-2 rounded-full bg-red-500 px-3 py-1.5 text-xs font-semibold text-white"
                      @click="finishLesson(lesson)">
                Завершить урок
              </button>
            </div>
          </div>
        </section>
      </template>
    </div>
  </AppLayout>
</template>
