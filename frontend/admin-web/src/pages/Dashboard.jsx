import { useEffect, useState } from 'react'
import api from '../api'

const CARDS = [
  { key: 'users', label: 'Пользователей', color: 'text-gray-900' },
  { key: 'students', label: 'Учеников', color: 'text-blue-600' },
  { key: 'teachers', label: 'Преподавателей', color: 'text-purple-600' },
  { key: 'pending_applications', label: 'Заявок преподавателей', color: 'text-amber-600' },
  { key: 'ai_sessions', label: 'AI-сессий', color: 'text-red-500' },
  { key: 'tasks_done', label: 'Заданий пройдено', color: 'text-green-600' },
]

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/admin/dashboard')
      .then(({ data }) => setStats(data))
      .catch((e) => console.log(e.response))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">Дашборд</h1>
      <p className="text-sm text-gray-400 mt-1">Сводная статистика платформы</p>

      {loading ? (
        <div className="py-24 text-center text-gray-400">Загрузка…</div>
      ) : (
        <div className="mt-6 grid grid-cols-2 md:grid-cols-3 gap-4">
          {CARDS.map((c) => (
            <div key={c.key} className="bg-white rounded-2xl border border-gray-100 p-5">
              <div className={`text-3xl font-bold ${c.color}`}>{stats?.[c.key] ?? 0}</div>
              <div className="text-sm text-gray-500 mt-1">{c.label}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
