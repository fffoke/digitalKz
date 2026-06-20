import { useEffect, useState } from 'react'
import api from '../api'

export default function Moderation() {
  const [tab, setTab] = useState('students')
  const [verifications, setVerifications] = useState([])
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [notes, setNotes] = useState({}) // applicationId -> note

  const load = async () => {
    setLoading(true)
    try {
      const [v, a] = await Promise.all([
        api.get('/admin/moderation/verifications'),
        api.get('/admin/moderation/teacher-applications'),
      ])
      setVerifications(v.data)
      setApplications(a.data)
    } catch (e) {
      console.log(e.response)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const act = async (url, body) => {
    try {
      await api.post(url, body)
      await load()
    } catch (e) {
      alert(e.response?.data?.detail || 'Ошибка')
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">Модерация</h1>
      <p className="text-sm text-gray-400 mt-1">Заявки преподавателей</p>


      {loading ? (
        <div className="py-24 text-center text-gray-400">Загрузка…</div>
      ) : (
        <div className="mt-5 space-y-3">
          {applications.length === 0 && <Empty text="Нет заявок преподавателей" />}
          {applications.map((a) => (
            <div key={a.id} className="bg-white rounded-2xl border border-gray-100 p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <p className="font-semibold text-gray-900">{a.user_name}
                    <span className="ml-2 px-2 py-0.5 rounded-full bg-purple-50 text-purple-600 text-xs">{a.kazakh_level || '—'}</span>
                  </p>
                  <p className="text-sm text-gray-400">{a.user_email}</p>
                </div>
              </div>
              <div className="mt-3 grid sm:grid-cols-2 gap-3 text-sm">
                <Field label="Образование" value={a.education} />
                <Field label="Опыт" value={a.experience} />
              </div>
              <textarea
                placeholder="Заметка по мини-собеседованию (необязательно)"
                value={notes[a.id] || ''}
                onChange={(e) => setNotes({ ...notes, [a.id]: e.target.value })}
                rows={2}
                className="mt-3 w-full rounded-xl border border-gray-200 bg-gray-50 px-3 py-2 text-sm focus:border-red-400 focus:outline-none resize-none"
              />
              <div className="mt-3 flex justify-end gap-2">
                <button onClick={() => act(`/admin/moderation/teacher-applications/${a.id}/reject`, { note: notes[a.id] })}
                  className="px-4 py-2 rounded-xl text-sm font-medium bg-gray-100 text-gray-600 hover:bg-gray-200">Отклонить</button>
                <button onClick={() => act(`/admin/moderation/teacher-applications/${a.id}/approve`, { note: notes[a.id] })}
                  className="px-4 py-2 rounded-xl text-sm font-semibold bg-green-500 text-white hover:bg-green-600">Одобрить</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function TabBtn({ active, onClick, children }) {
  return (
    <button onClick={onClick}
      className={`px-4 py-2 rounded-xl text-sm font-medium transition ${active ? 'bg-red-500 text-white' : 'bg-white border border-gray-200 text-gray-600'
        }`}>
      {children}
    </button>
  )
}
function Badge({ n }) {
  if (!n) return null
  return <span className="ml-1 inline-flex items-center justify-center min-w-5 h-5 px-1 rounded-full bg-black/10 text-xs">{n}</span>
}
function Empty({ text }) {
  return <div className="bg-white rounded-2xl border border-gray-100 py-16 text-center text-gray-400 text-sm">{text}</div>
}
function Field({ label, value }) {
  return (
    <div className="bg-gray-50 rounded-xl p-3">
      <p className="text-xs text-gray-400">{label}</p>
      <p className="text-gray-700 mt-0.5">{value || '—'}</p>
    </div>
  )
}
