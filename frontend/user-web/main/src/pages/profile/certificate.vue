<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMyProfile } from '@/services/users'

const router = useRouter()
const profile = ref(null)
const loading = ref(true)

onMounted(async () => {
  try { profile.value = (await getMyProfile()).data }
  catch (e) { console.log(e.response) }
  finally { loading.value = false }
})

const KK_MONTHS = ['қаңтар', 'ақпан', 'наурыз', 'сәуір', 'мамыр', 'маусым',
  'шілде', 'тамыз', 'қыркүйек', 'қазан', 'қараша', 'желтоқсан']
const kkDate = (d) => `${d.getDate()} ${KK_MONTHS[d.getMonth()]} ${d.getFullYear()} ж.`

const now = new Date()
const validTo = new Date(now.getFullYear() + 2, now.getMonth(), now.getDate())

const issued = kkDate(now)
const valid = kkDate(validTo)
const level = computed(() => profile.value?.level || 'A1')
const rank = computed(() => profile.value?.rank || 'Бастауыш')
const name = computed(() => profile.value?.name || 'Аты-жөні')
const number = computed(() =>
  `TLDS-${now.getFullYear()}-${String(profile.value?.id || 0).padStart(5, '0')}`)

const download = () => window.print()
const back = () => router.push({ name: 'profile' })
</script>

<template>
  <div class="min-h-screen bg-gray-100 dark:bg-neutral-950 flex flex-col items-center">
    <!-- панель (не печатается) -->
    <div class="no-print w-full max-w-4xl flex items-center justify-between px-4 py-3">
      <button class="text-sm text-gray-500 dark:text-gray-300" @click="back">← Назад</button>
      <button class="bg-red-500 hover:bg-red-600 text-white text-sm font-semibold rounded-xl px-5 py-2.5"
              @click="download">⬇ Скачать сертификат (PDF)</button>
    </div>

    <div v-if="loading" class="py-24 text-gray-400">Загрузка…</div>

    <!-- сам сертификат -->
    <div v-else class="cert-wrap px-3 pb-10 w-full flex justify-center">
      <div class="cert relative bg-white text-gray-900 rounded-2xl border border-gray-200 shadow-xl
                  w-full max-w-4xl aspect-[1.41/1] overflow-hidden">
        <!-- декоративные волны -->
        <div class="absolute -bottom-24 -right-24 w-96 h-96 rounded-full border border-gray-100"></div>
        <div class="absolute -bottom-32 -right-32 w-[28rem] h-[28rem] rounded-full border border-gray-100"></div>

        <div class="relative h-full p-[5%] flex flex-col">
          <!-- шапка -->
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-2">
              <div class="w-9 h-9 rounded-lg bg-red-500 text-white flex items-center justify-center font-bold">Т</div>
              <span class="font-bold tracking-wide">ТІЛДЕС</span>
            </div>
            <span class="text-xs text-gray-500 border border-gray-200 rounded-full px-3 py-1">№ {{ number }}</span>
          </div>

          <!-- заголовок -->
          <h1 class="mt-[3%] text-5xl sm:text-6xl font-extrabold tracking-tight leading-none">СЕРТИФИКАТ</h1>
          <p class="mt-2 text-gray-500 text-sm sm:text-base">Қазақ тілін меңгеру деңгейін растайды</p>

          <!-- имя -->
          <div class="mt-[4%] max-w-[60%]">
            <p class="text-[11px] tracking-widest text-gray-400">ОСЫ СЕРТИФИКАТ</p>
            <p class="mt-1 text-2xl sm:text-3xl font-bold border-b border-gray-300 pb-2">{{ name }}</p>
            <p class="mt-3 text-sm text-gray-600 leading-relaxed">
              ТІЛДЕС платформасында қазақ тілін оқып, тестілеуден өтіп,
              төмендегі деңгейге қол жеткізгенін растайды.
            </p>
          </div>

          <!-- даты -->
          <div class="mt-auto flex gap-10">
            <div>
              <p class="text-[11px] tracking-widest text-gray-400">БЕРІЛГЕН КҮНІ</p>
              <p class="mt-1 font-medium">{{ issued }}</p>
            </div>
            <div class="border-l border-gray-200 pl-10">
              <p class="text-[11px] tracking-widest text-gray-400">ЖАРАМДЫЛЫҚ МЕРЗІМІ</p>
              <p class="mt-1 font-medium">{{ valid }}</p>
            </div>
          </div>

          <!-- подпись -->
          <div class="mt-[4%] w-56">
            <p class="signature text-2xl text-gray-700 leading-none">Berik</p>
            <div class="border-t border-gray-800 mt-1 pt-1">
              <p class="font-bold text-sm">Бактыбай Берік</p>
              <p class="text-xs text-gray-500">ТІЛДЕС негізін қалаушысы</p>
            </div>
          </div>

          <!-- правый блок: уровень/ранг -->
          <div class="absolute top-[18%] right-[6%] w-40 rounded-2xl border border-gray-200 text-center py-4">
            <p class="text-[11px] tracking-widest text-gray-400">ДЕҢГЕЙ</p>
            <p class="text-5xl font-extrabold text-red-500 leading-none mt-1">{{ level }}</p>
            <div class="border-t border-gray-200 my-3 mx-4"></div>
            <p class="text-[11px] tracking-widest text-gray-400">РАНГ</p>
            <p class="text-xl font-bold mt-1">{{ rank }}</p>
          </div>

          <!-- печать -->
          <div class="absolute bottom-[8%] right-[8%] w-28 h-28 rounded-full border-[3px] border-red-500/80
                      flex items-center justify-center text-center">
            <div class="w-20 h-20 rounded-full border border-red-400/60 flex flex-col items-center justify-center">
              <div class="w-7 h-7 rounded-md bg-red-500 text-white flex items-center justify-center text-xs font-bold">Т</div>
              <span class="mt-1 text-[8px] font-bold text-red-500 tracking-wider">ТІЛДЕС</span>
              <span class="text-[7px] text-red-400">TILDES.KZ</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.signature {
  font-family: 'Brush Script MT', 'Segoe Script', cursive;
  font-style: italic;
}
@media print {
  @page { size: landscape; margin: 0; }
  .no-print { display: none !important; }
  .cert-wrap { padding: 0 !important; }
  .cert {
    box-shadow: none !important;
    border: none !important;
    border-radius: 0 !important;
    max-width: 100% !important;
    width: 100% !important;
  }
}
</style>
