<script setup>
import { computed, onMounted, ref } from 'vue'

import AppLayout from '@/components/layout/AppLayout.vue'
import { getRoleStatus, submitVerification, applyTeacher } from '@/services/onboarding'
import {
  completeLesson,
  createGroup,
  getLearningOverview,
  gradeHomework,
  joinGroup,
  joinGroupByCode,
  rateLesson,
  scheduleLesson,
  submitEntranceTest,
  submitHomework,
  submitLevelExam,
} from '@/services/learning'

const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const mode = ref('choose')
const status = ref(null)
const overview = ref(null)

const iin = ref('')
const teacherForm = ref({ education: '', experience: '', kazakh_level: 'B2' })
const testAnswers = ref({})
const listeningAnswers = ref({ l1: '', l2: '', l3: '' })
const readingText = ref('')
const groupForm = ref({ name: '', schedule: 'three_week' })
const inviteCode = ref('')
const lessonStarts = ref('')
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
  if (!lessonStarts.value) {
    error.value = 'Выберите дату и время урока'
    return
  }
  submitting.value = true
  error.value = ''
  try {
    await scheduleLesson(group.id, new Date(lessonStarts.value).toISOString())
    lessonStarts.value = ''
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось запланировать урок'
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
            25 вопросов, 3 задания на слух и текст чтения. В прототипе результат считается автоматически.
          </p>
          <div class="mt-4 grid grid-cols-5 gap-2">
            <button
              v-for="i in 25"
              :key="i"
              class="rounded-lg border px-2 py-2 text-xs"
              :class="answerValue(i) ? 'border-red-500 bg-red-50 text-red-600' : 'border-gray-200 text-gray-500 dark:border-neutral-700'"
              @click="setAnswer(i, answerValue(i) ? '' : 'a')"
            >
              {{ i }}
            </button>
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
          <section v-if="currentGroup" class="rounded-2xl border border-gray-100 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900">
            <h3 class="font-bold text-gray-900 dark:text-white">{{ currentGroup.name }}</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {{ currentGroup.level }} · {{ schedules[currentGroup.schedule] }} · {{ currentGroup.members_count }}/5 участников
            </p>
            <p class="mt-3 rounded-xl bg-gray-50 px-3 py-2 text-xs text-gray-500 dark:bg-neutral-800 dark:text-gray-300">
              Ссылка для друзей: {{ currentGroup.invite_code }}
            </p>
          </section>

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

          <section v-if="overview?.progress?.length" class="rounded-2xl border border-gray-100 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900">
            <h3 class="font-bold text-gray-900 dark:text-white">Карта прогресса</h3>
            <div class="mt-4 grid grid-cols-3 gap-2">
              <div v-for="stage in overview.progress" :key="`${stage.section}-${stage.stage}`"
                   class="rounded-xl border p-3 text-xs"
                   :class="stage.status === 'done' ? 'border-green-200 bg-green-50 text-green-700' : stage.status === 'current' ? 'border-red-200 bg-red-50 text-red-600' : 'border-gray-200 text-gray-400 dark:border-neutral-700'">
                {{ stage.title }}
              </div>
            </div>
          </section>

          <section class="rounded-2xl border border-gray-100 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900">
            <h3 class="font-bold text-gray-900 dark:text-white">Экзамен на повышение</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              20 вопросов и голосовое чтение. При результате от 70% уровень повышается.
            </p>
            <div class="mt-4 grid grid-cols-5 gap-2">
              <button
                v-for="i in 20"
                :key="i"
                class="rounded-lg border px-2 py-2 text-xs"
                :class="levelExamAnswers[`q${i}`] ? 'border-red-500 bg-red-50 text-red-600' : 'border-gray-200 text-gray-500 dark:border-neutral-700'"
                @click="levelExamAnswers[`q${i}`] = levelExamAnswers[`q${i}`] ? '' : 'a'"
              >
                {{ i }}
              </button>
            </div>
            <textarea v-model="levelReadingText" rows="2" placeholder="Текст голосового задания"
              class="mt-3 w-full rounded-xl border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm dark:border-neutral-700 dark:bg-neutral-800 dark:text-white" />
            <button class="mt-3 w-full rounded-xl bg-red-500 py-3 text-sm font-semibold text-white"
                    @click="finishLevelExam">
              Сдать экзамен
            </button>
          </section>
        </template>

        <section v-if="isTeacher" class="rounded-2xl border border-gray-100 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900">
          <h3 class="font-bold text-gray-900 dark:text-white">Группы без преподавателя</h3>
          <input v-model="lessonStarts" type="datetime-local"
            class="mt-3 w-full rounded-xl border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm dark:border-neutral-700 dark:bg-neutral-800 dark:text-white">
          <div class="mt-3 space-y-2">
            <div v-for="group in overview?.open_teacher_groups" :key="group.id"
                 class="rounded-xl border border-gray-100 p-3 dark:border-neutral-800">
              <div class="flex items-center justify-between gap-2">
                <div>
                  <p class="font-semibold text-gray-900 dark:text-white">{{ group.name }}</p>
                  <p class="text-xs text-gray-500">{{ group.level }} · секция {{ group.current_section }}, этап {{ group.current_stage }} · {{ group.members_count }}/5</p>
                </div>
                <button class="rounded-xl bg-red-500 px-3 py-2 text-xs font-semibold text-white"
                        @click="planLesson(group)">Взять</button>
              </div>
            </div>
            <p v-if="!overview?.open_teacher_groups?.length" class="py-4 text-center text-sm text-gray-400">
              Пока нет групп, готовых к уроку.
            </p>
          </div>
        </section>

        <section v-if="overview?.lessons?.length" class="rounded-2xl border border-gray-100 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900">
          <h3 class="font-bold text-gray-900 dark:text-white">Уроки</h3>
          <div class="mt-3 space-y-3">
            <div v-for="lesson in overview.lessons" :key="lesson.id" class="rounded-xl bg-gray-50 p-3 dark:bg-neutral-800">
              <p class="font-semibold text-gray-900 dark:text-white">{{ new Date(lesson.starts_at).toLocaleString() }}</p>
              <p class="text-xs text-gray-500">{{ lessonStatus[lesson.status] }}</p>
              <a v-if="lesson.meet_link" :href="lesson.meet_link" target="_blank"
                 class="mt-2 inline-flex rounded-full bg-white px-3 py-1.5 text-xs font-semibold text-red-600 dark:bg-neutral-900">
                Открыть Google Meet
              </a>
              <button v-if="isTeacher && lesson.status !== 'completed'"
                      class="ml-2 rounded-full bg-red-500 px-3 py-1.5 text-xs font-semibold text-white"
                      @click="finishLesson(lesson)">
                Завершить урок
              </button>
              <div v-if="isStudent && lesson.status === 'completed'" class="mt-3 grid gap-2 sm:grid-cols-[90px_1fr_auto]">
                <select v-model="ensureRatingDraft(lesson).score"
                  class="rounded-xl border border-gray-200 bg-white px-2 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900 dark:text-white">
                  <option v-for="score in [5,4,3,2,1]" :key="score" :value="score">{{ score }}</option>
                </select>
                <input v-model="ensureRatingDraft(lesson).review" placeholder="Отзыв"
                  class="rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900 dark:text-white">
                <button class="rounded-xl bg-red-500 px-3 py-2 text-sm font-semibold text-white"
                        @click="sendRating(lesson)">Оценить</button>
              </div>
            </div>
          </div>
        </section>

        <section v-if="overview?.homeworks?.length" class="rounded-2xl border border-gray-100 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900">
          <h3 class="font-bold text-gray-900 dark:text-white">Домашние задания</h3>
          <div class="mt-3 space-y-3">
            <div v-for="homework in overview.homeworks" :key="homework.id" class="rounded-xl bg-gray-50 p-3 dark:bg-neutral-800">
              <p class="text-sm text-gray-800 dark:text-gray-100">{{ homework.task }}</p>
              <p class="mt-1 text-xs text-gray-500">{{ homeworkStatus[homework.status] }}</p>
              <div v-if="isStudent && homework.status === 'assigned'" class="mt-3 flex gap-2">
                <input v-model="homeworkDrafts[homework.id]" placeholder="Ответ на ДЗ"
                  class="min-w-0 flex-1 rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900 dark:text-white">
                <button class="rounded-xl bg-red-500 px-3 py-2 text-sm font-semibold text-white"
                        @click="sendHomework(homework)">Отправить</button>
              </div>
              <div v-if="isTeacher && homework.status === 'submitted'" class="mt-3 grid gap-2 sm:grid-cols-[90px_1fr_auto]">
                <input v-model.number="ensureGradeDraft(homework).grade" type="number" min="1" max="100"
                  class="rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900 dark:text-white">
                <input v-model="ensureGradeDraft(homework).feedback" placeholder="Комментарий"
                  class="rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900 dark:text-white">
                <button class="rounded-xl bg-red-500 px-3 py-2 text-sm font-semibold text-white"
                        @click="sendGrade(homework)">Проверить</button>
              </div>
            </div>
          </div>
        </section>
      </template>
    </div>
  </AppLayout>
</template>
