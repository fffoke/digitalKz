import { NavLink } from 'react-router-dom'

const nav = [
  { to: '/', label: 'Дашборд', end: true },
  { to: '/moderation', label: 'Модерация' },
  { to: '/materials', label: 'Материалы' },
  { to: '/exams', label: 'Экзамены' },
]

export default function Layout({ user, onLogout, children }) {
  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* sidebar */}
      <aside className="w-60 shrink-0 bg-white border-r border-gray-100 flex flex-col">
        <div className="h-16 flex items-center gap-2.5 px-5 border-b border-gray-100">
          <div className="w-8 h-8 rounded-lg bg-red-500 text-white flex items-center justify-center font-bold">T</div>
          <span className="font-semibold">ТІЛДЕС Админ</span>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {nav.map((n) => (
            <NavLink
              key={n.to} to={n.to} end={n.end}
              className={({ isActive }) =>
                `block px-3 py-2.5 rounded-xl text-sm font-medium transition ${isActive ? 'bg-red-50 text-red-600' : 'text-gray-500 hover:bg-gray-50'
                }`
              }
            >
              {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 border-t border-gray-100">
          <p className="px-3 text-xs text-gray-400 truncate">{user.email}</p>
          <button
            onClick={onLogout}
            className="mt-2 w-full text-left px-3 py-2 rounded-xl text-sm text-gray-500 hover:bg-gray-50"
          >
            Выйти
          </button>
        </div>
      </aside>

      {/* content */}
      <main className="flex-1 min-w-0">
        <div className="max-w-5xl mx-auto p-6">{children}</div>
      </main>
    </div>
  )
}
