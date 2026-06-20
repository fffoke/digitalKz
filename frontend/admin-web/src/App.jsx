import { useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import api from './api'
import Login from './pages/Login.jsx'
import Layout from './components/Layout.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Moderation from './pages/Moderation.jsx'
import Materials from "./pages/Material.jsx";

export default function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const loadMe = async () => {
    try {
      const { data } = await api.get('/auth/me')
      setUser(data.role === 'admin' ? data : null)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (localStorage.getItem('admin_token')) loadMe()
    else setLoading(false)
  }, [])

  const logout = () => {
    localStorage.removeItem('admin_token')
    setUser(null)
  }

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-gray-400">Загрузка…</div>
  }

  if (!user) {
    return (
      <Routes>
        <Route path="*" element={<Login onSuccess={loadMe} />} />
      </Routes>
    )
  }

  return (
    <Layout user={user} onLogout={logout}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/moderation" element={<Moderation />} />
        <Route path="/materials" element={<Materials />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}
