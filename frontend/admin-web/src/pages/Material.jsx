import { useEffect, useState } from 'react'
import api from '../api'

const LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1']
const blank = () => ({ level: 'A1', section: 1, stage: 1, title: '', content: '' })

export default function Materials() {
  const [items, setItems] = useState([])
  const [filter, setFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState(blank())
  const [editingId, setEditingId] = useState(null)
  const [saving, setSaving] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const { data } = await api.get('/admin/materials', { params: filter ? { level: filter } : {} })
      setItems(data)
    } catch (e) { console.log(e.response) } finally { setLoading(false) }
  }
  useEffect(() => { load() }, [filter])

  const edit = (m) => { setEditingId(m.id); setForm({ ...m }) }
  const reset = () => { setEditingId(null); setForm(blank()) }

  const save = async () => {
    if (!form.title.trim() || !form.content.trim()) { alert('Заполните название и содержание'); return }
    setSaving(true)
    try {
      const payload = {
        level: form.level,
        section: form.section ? Number(form.section) : null,
        stage: form.stage ? Number(form.stage) : null,
        title: form.title, content: form.content,
      }
      if (editingId) await api.put(`/admin/materials/${editingId}`, payload)
      else await api.post('/admin/materials', payload)
      reset(); await load()
    } catch (e) { alert(e.response?.data?.detail || 'Ошибка') } finally { setSaving(false) }
  }

  const remove = async (m) => {
    if (!confirm(`Удалить «${m.title}»?`)) return
    try { await api.delete(`/admin/materials/${m.id}`); await load() }
    catch (e) { alert(e.response?.data?.detail || 'Ошибка') }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">Материалы</h1>
      <p className="text-sm text-gray-400 mt-1">Учебные материалы по уровням для учеников</p>

      <div className="mt-5 grid md:grid-cols-2 gap-5">
        {/* форма */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5 space-y-3 h-fit">
          <h2 className="font-semibold text-gray-900">{editingId ? 'Редактирование' : 'Новый материал'}</h2>
          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Уровень</label>
              <select value={form.level} onChange={(e) => setForm({ ...form, level: e.target.value })}
                className="w-full rounded-xl border border-gray-200 bg-gray-50 px-2 py-2 text-sm">
                {LEVELS.map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Секция</label>
              <input type="number" min="1" value={form.section || ''} onChange={(e) => setForm({ ...form, section: e.target.value })}
                className="w-full rounded-xl border border-gray-200 bg-gray-50 px-2 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Этап</label>
              <input type="number" min="1" value={form.stage || ''} onChange={(e) => setForm({ ...form, stage: e.target.value })}
                className="w-full rounded-xl border border-gray-200 bg-gray-50 px-2 py-2 text-sm" />
            </div>
          </div>
          <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="Название" className="w-full rounded-xl border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm focus:border-red-400 focus:outline-none" />
          <textarea value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })}
            rows={6} placeholder="Содержание (лексика, фразы, правила…)"
            className="w-full rounded-xl border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm focus:border-red-400 focus:outline-none resize-none" />
          <div className="flex gap-2">
            <button onClick={save} disabled={saving}
              className="flex-1 bg-red-500 hover:bg-red-600 disabled:opacity-50 text-white rounded-xl py-2.5 text-sm font-semibold">
              {saving ? 'Сохраняем…' : editingId ? 'Сохранить' : 'Добавить'}
            </button>
            {editingId && <button onClick={reset} className="px-4 rounded-xl bg-gray-100 text-gray-600 text-sm">Отмена</button>}
          </div>
        </div>

        {/* список */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <select value={filter} onChange={(e) => setFilter(e.target.value)}
              className="rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm">
              <option value="">Все уровни</option>
              {LEVELS.map((l) => <option key={l} value={l}>{l}</option>)}
            </select>
            <span className="text-sm text-gray-400">{items.length} материалов</span>
          </div>

          {loading ? (
            <div className="py-16 text-center text-gray-400">Загрузка…</div>
          ) : items.length === 0 ? (
            <div className="bg-white rounded-2xl border border-gray-100 py-12 text-center text-gray-400 text-sm">Материалов нет</div>
          ) : (
            <div className="space-y-2">
              {items.map((m) => (
                <div key={m.id} className="bg-white rounded-2xl border border-gray-100 p-4">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 text-xs font-medium">{m.level}</span>
                        <span className="text-xs text-gray-400">секция {m.section || '—'}, этап {m.stage || '—'}</span>
                      </div>
                      <p className="font-semibold text-gray-900 mt-1">{m.title}</p>
                      <p className="text-sm text-gray-500 mt-0.5 line-clamp-2">{m.content}</p>
                    </div>
                    <div className="flex shrink-0 gap-1">
                      <button onClick={() => edit(m)} className="p-1.5 rounded-lg text-gray-400 hover:bg-gray-100">✏️</button>
                      <button onClick={() => remove(m)} className="p-1.5 rounded-lg text-gray-400 hover:bg-red-50 hover:text-red-500">🗑</button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
