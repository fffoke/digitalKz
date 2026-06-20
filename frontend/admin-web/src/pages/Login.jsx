import { useState } from 'react'
import api from '../api'

export default function Login({ onSuccess }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { data } = await api.post('/auth/login', { email, password })
      localStorage.setItem('admin_token', data.access_token)
      // проверим, что это админ
      const me = await api.get('/auth/me')
      if (me.data.role !== 'admin') {
        localStorage.removeItem('admin_token')
        setError('Этот аккаунт не администратор')
        return
      }
      onSuccess()
    } catch (err) {
      setError(err.response?.data?.detail || 'Неверный email или пароль')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <form onSubmit={submit} className="w-full max-w-sm bg-white rounded-2xl border border-gray-100 shadow-sm p-6 space-y-4">
        <div className="text-center">
          <div className="mx-auto w-11 h-11 rounded-xl bg-red-500 text-white flex items-center justify-center font-bold text-lg">T</div>
          <h1 className="mt-3 text-lg font-bold text-gray-900">Админ-панель ТІЛДЕС</h1>
          <p className="text-sm text-gray-400">Вход для администратора</p>
        </div>

        <input
          type="email" placeholder="Email" value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-3 text-sm focus:border-red-400 focus:outline-none"
        />
        <input
          type="password" placeholder="Пароль" value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-3 text-sm focus:border-red-400 focus:outline-none"
        />

        {error && <p className="text-sm text-red-500 text-center">{error}</p>}

        <button
          disabled={loading}
          className="w-full bg-red-500 hover:bg-red-600 disabled:opacity-50 text-white font-semibold rounded-xl py-3 text-sm transition"
        >
          {loading ? 'Входим…' : 'Войти'}
        </button>
      </form>
    </div>
  )
}
