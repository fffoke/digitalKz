import { useEffect, useState } from 'react'
import api from '../api'
import AudioRecorder from '../components/AudioRecorder.jsx'

const TYPES = [
  { value: 'choice', label: 'Выбор варианта' },
  { value: 'listening', label: 'Аудирование (ответ текстом)' },
  { value: 'reading', label: 'Чтение / голос' },
]
const NEXT_LEVELS = ['A2', 'B1', 'B2', 'C1']
const emptyQuestion = () => ({ type: 'choice', text: '', options: ['', ''], answer: '', audio_url: '' })

export default function Exams() {
  const [options, setOptions] = useState([{ key: 'entrance', label: 'Вступительный тест' }])
  const [selected, setSelected] = useState('entrance')
  const [exam, setExam] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [uploadingId, setUploadingId] = useState(null)

  const uploadAudio = async (qi, blob, filename) => {
    setUploadingId(qi)
    try {
      const fd = new FormData()
      fd.append('file', blob, filename)
      const { data } = await api.post('/admin/exams/upload-audio', fd)
      updateQ(qi, { audio_url: data.url })
    } catch (e) {
      alert(e.response?.data?.detail || 'Не удалось загрузить аудио')
    } finally {
      setUploadingId(null)
    }
  }

  const loadList = async () => {
    const { data } = await api.get('/admin/exams')   // level-экзамены
    const opts = [{ key: 'entrance', label: 'Вступительный тест' }]
    data.forEach((e) => opts.push({ key: `level-${e.id}`, id: e.id, label: `Экзамен → ${e.target_level || '?'}` }))
    setOptions(opts)
    return opts
  }

  const loadExam = async (key) => {
    setLoading(true); setSaved(false)
    try {
      const url = key === 'entrance' ? '/admin/exams/entrance' : `/admin/exams/${key.split('-')[1]}`
      const { data } = await api.get(url)
      setExam({ title: data.title || '', voice_task: data.voice_task || '', questions: data.questions || [] })
    } catch (e) { console.log(e.response) } finally { setLoading(false) }
  }

  useEffect(() => { loadList().then(() => loadExam('entrance')) }, [])

  const onSelect = (key) => { setSelected(key); loadExam(key) }

  const createLevelExam = async () => {
    const lvl = prompt('Экзамен на повышение ДО уровня (A2 / B1 / B2 / C1):', 'A2')
    if (!lvl || !NEXT_LEVELS.includes(lvl.trim().toUpperCase())) {
      if (lvl) alert('Уровень должен быть A2, B1, B2 или C1')
      return
    }
    const target = lvl.trim().toUpperCase()
    const { data } = await api.post('/admin/exams', {
      title: `Экзамен на ${target}`, target_level: target, questions: [],
      voice_task: 'Прочитайте короткий текст на казахском вслух.',
    })
    await loadList()
    setSelected(`level-${data.id}`); loadExam(`level-${data.id}`)
  }

  const update = (patch) => setExam((e) => ({ ...e, ...patch }))
  const updateQ = (i, patch) => update({ questions: exam.questions.map((q, idx) => (idx === i ? { ...q, ...patch } : q)) })
  const addQ = () => update({ questions: [...exam.questions, emptyQuestion()] })
  const removeQ = (i) => update({ questions: exam.questions.filter((_, idx) => idx !== i) })
  const setOption = (qi, oi, v) => updateQ(qi, { options: exam.questions[qi].options.map((o, idx) => (idx === oi ? v : o)) })
  const addOption = (qi) => updateQ(qi, { options: [...(exam.questions[qi].options || []), ''] })
  const removeOption = (qi, oi) => updateQ(qi, { options: exam.questions[qi].options.filter((_, idx) => idx !== oi) })

  const save = async () => {
    setSaving(true); setSaved(false)
    try {
      const payload = {
        title: exam.title,
        voice_task: exam.voice_task,
        questions: exam.questions.map((q) => ({
          type: q.type, text: q.text,
          options: q.type === 'choice' ? (q.options || []).filter((o) => o.trim()) : [],
          answer: q.answer || null,
          audio_url: q.type === 'listening' ? (q.audio_url || null) : null,
        })),
      }
      const url = selected === 'entrance' ? '/admin/exams/entrance' : `/admin/exams/${selected.split('-')[1]}`
      const { data } = await api.put(url, payload)
      setExam({ title: data.title, voice_task: data.voice_task || '', questions: data.questions || [] })
      setSaved(true)
    } catch (e) {
      alert(e.response?.data?.detail || 'Ошибка сохранения')
    } finally { setSaving(false) }
  }

  return (
    <div>
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Экзамены</h1>
          <p className="text-sm text-gray-400 mt-1">Выберите экзамен для редактирования</p>
        </div>
        <button onClick={save} disabled={saving || !exam}
          className="px-5 py-2.5 rounded-xl bg-red-500 hover:bg-red-600 disabled:opacity-50 text-white text-sm font-semibold">
          {saving ? 'Сохраняем…' : 'Сохранить'}
        </button>
      </div>

      {/* селектор экзамена */}
      <div className="mt-4 flex items-center gap-2 flex-wrap">
        <select value={selected} onChange={(e) => onSelect(e.target.value)}
          className="rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm min-w-56">
          {options.map((o) => <option key={o.key} value={o.key}>{o.label}</option>)}
        </select>
        <button onClick={createLevelExam}
          className="px-4 py-2.5 rounded-xl bg-gray-900 text-white text-sm font-medium">＋ Экзамен на уровень</button>
      </div>
      {saved && <p className="mt-2 text-sm text-green-600">Сохранено ✓</p>}

      {loading || !exam ? (
        <div className="py-24 text-center text-gray-400">Загрузка…</div>
      ) : (
        <>
          {/* голосовое задание */}
          <div className="mt-5 bg-white rounded-2xl border border-gray-100 p-5">
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Голосовое задание (чтение)</label>
            <textarea rows={2} value={exam.voice_task} onChange={(e) => update({ voice_task: e.target.value })}
              placeholder="Текст, который ученик прочитает голосом"
              className="w-full rounded-xl border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm focus:border-red-400 focus:outline-none resize-none" />
          </div>

          {/* вопросы */}
          <div className="mt-5 flex items-center justify-between">
            <h2 className="font-semibold text-gray-900">Вопросы ({exam.questions.length})</h2>
            <button onClick={addQ} className="px-4 py-2 rounded-xl bg-gray-900 text-white text-sm font-medium">＋ Добавить вопрос</button>
          </div>

          <div className="mt-3 space-y-3">
            {exam.questions.length === 0 && (
              <div className="bg-white rounded-2xl border border-gray-100 py-12 text-center text-gray-400 text-sm">
                Пока нет вопросов — добавьте первый
              </div>
            )}

            {exam.questions.map((q, i) => (
              <div key={i} className="bg-white rounded-2xl border border-gray-100 p-5">
                <div className="flex items-start justify-between gap-3">
                  <span className="shrink-0 w-7 h-7 rounded-full bg-gray-100 text-gray-500 text-sm flex items-center justify-center">{i + 1}</span>
                  <div className="flex-1 space-y-3">
                    <input value={q.text} onChange={(e) => updateQ(i, { text: e.target.value })}
                      placeholder="Текст вопроса"
                      className="w-full rounded-xl border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm focus:border-red-400 focus:outline-none" />
                    <select value={q.type} onChange={(e) => updateQ(i, { type: e.target.value })}
                      className="rounded-xl border border-gray-200 bg-gray-50 px-3 py-2 text-sm focus:border-red-400 focus:outline-none">
                      {TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                    </select>

                    {q.type === 'listening' && (
                      <div className="space-y-2">
                        <p className="text-xs text-gray-500">Аудио, которое слушает ученик:</p>
                        {q.audio_url && <audio src={q.audio_url} controls className="w-full h-9" />}
                        <div className="flex items-center gap-2 flex-wrap">
                          <label className="px-3 py-2 rounded-lg bg-gray-100 text-gray-700 text-sm font-medium cursor-pointer">
                            📎 Загрузить файл
                            <input type="file" accept="audio/*" className="hidden"
                              onChange={(e) => { const f = e.target.files[0]; if (f) uploadAudio(i, f, f.name) }} />
                          </label>
                          <AudioRecorder disabled={uploadingId === i} onRecorded={(b) => uploadAudio(i, b, 'record.webm')} />
                          {uploadingId === i && <span className="text-xs text-gray-400">загрузка…</span>}
                        </div>
                        <input value={q.answer || ''} onChange={(e) => updateQ(i, { answer: e.target.value })}
                          placeholder="Что должно быть услышано (правильный текст)"
                          className="w-full rounded-lg border border-green-200 bg-green-50 px-3 py-2 text-sm focus:border-green-400 focus:outline-none" />
                      </div>
                    )}

                    {q.type === 'choice' && (
                      <div className="space-y-2">
                        {(q.options || []).map((o, oi) => (
                          <div key={oi} className="flex items-center gap-2">
                            <input value={o} onChange={(e) => setOption(i, oi, e.target.value)}
                              placeholder={`Вариант ${oi + 1}`}
                              className="flex-1 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm focus:border-red-400 focus:outline-none" />
                            <button onClick={() => removeOption(i, oi)} className="text-gray-300 hover:text-red-500 px-2">✕</button>
                          </div>
                        ))}
                        <button onClick={() => addOption(i)} className="text-sm text-gray-500 hover:text-red-500">＋ вариант</button>
                        <input value={q.answer || ''} onChange={(e) => updateQ(i, { answer: e.target.value })}
                          placeholder="Правильный ответ (точный текст варианта)"
                          className="w-full rounded-lg border border-green-200 bg-green-50 px-3 py-2 text-sm focus:border-green-400 focus:outline-none" />
                      </div>
                    )}
                  </div>
                  <button onClick={() => removeQ(i)} className="shrink-0 text-gray-300 hover:text-red-500 px-1" title="Удалить вопрос">🗑</button>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
